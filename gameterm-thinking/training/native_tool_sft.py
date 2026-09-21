"""Reproducible completion-only LoRA training for native tool conversations.

The dataset owns examples and per-example tool visibility. The captured envelope
owns the system messages and complete schemas. The model's own chat template owns
the wire format. This module owns validation, rendering, feature caching, LoRA
initialization, optimization, and run provenance.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
import subprocess
import time

import numpy as np
import jsonschema

from daycare.learning.process import write_json
from daycare.model.chat_format import NativeToolChat
from daycare.model.decoder_forward import block_forward, validate_model


SCHEMA = "daycare.native_tool_sft.v1"
FULL_PRECISION_GGUF_TYPES = {1: "f16", 32: "bf16"}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_revision() -> str:
    root = Path(__file__).resolve().parents[2]
    if subprocess.check_output(["git", "-C", str(root), "status", "--porcelain",
                                "--untracked-files=no"]).decode().strip():
        raise ValueError("commit tracked DayCare changes before training")
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().strip()


def target_message(target: dict) -> dict:
    if target["kind"] == "words":
        return {"role": "assistant", "content": target["content"]}
    return {"role": "assistant", "content": "", "tool_calls": [{
        "id": "call_training", "type": "function",
        "function": {"name": target["name"], "arguments": target["arguments"]},
    }]}


def validate_call(call: dict, names: list[str], available: dict, context: str) -> str:
    function = call.get("function", {}) if isinstance(call, dict) else {}
    name, arguments = function.get("name"), function.get("arguments")
    if (not isinstance(call, dict) or call.get("type") != "function"
            or name not in names or not isinstance(arguments, dict)):
        raise ValueError(f"{context}: tool call must select a visible function with object arguments")
    jsonschema.validate(arguments, available[name]["function"]["parameters"])
    call_id = call.get("id")
    if not isinstance(call_id, str) or not call_id:
        raise ValueError(f"{context}: tool call id must be a nonempty string")
    return call_id


def validate_history(row: dict, names: list[str], available: dict) -> None:
    history = row.get("history", [])
    if not isinstance(history, list):
        raise ValueError(f"{row['id']}: history must be a list")
    for offset in range(0, len(history), 2):
        if offset + 1 >= len(history):
            raise ValueError(f"{row['id']}: history must end with a tool result")
        assistant, tool = history[offset:offset + 2]
        if not isinstance(assistant, dict) or assistant.get("role") != "assistant":
            raise ValueError(f"{row['id']}: history must alternate assistant calls and tool results")
        calls = assistant.get("tool_calls")
        if not isinstance(calls, list) or len(calls) != 1:
            raise ValueError(f"{row['id']}: each historical assistant turn must contain one tool call")
        call_id = validate_call(calls[0], names, available, f"{row['id']} history")
        if assistant.get("content") not in (None, ""):
            raise ValueError(f"{row['id']}: historical tool-call content must be empty")
        if (not isinstance(tool, dict) or tool.get("role") != "tool"
                or tool.get("tool_call_id") != call_id
                or not isinstance(tool.get("content"), str) or not tool["content"]):
            raise ValueError(f"{row['id']}: tool result must match its call id and contain text")


def load_dataset(path: Path, envelope: dict) -> tuple[dict, list[dict]]:
    dataset = json.loads(path.read_text())
    if dataset.get("schema") != SCHEMA or not isinstance(dataset.get("rows"), list):
        raise ValueError(f"dataset must use {SCHEMA}")
    if not isinstance(dataset.get("seed"), int) or isinstance(dataset.get("seed"), bool):
        raise ValueError("dataset seed must be an integer")
    if dataset.get("envelope_sha256") != file_sha256(Path(dataset["envelope"])):
        raise ValueError("dataset envelope hash does not match its declared source")
    available = {tool["function"]["name"]: tool for tool in envelope["tools"]}
    identifiers = set()
    for row in dataset["rows"]:
        if not isinstance(row.get("id"), str) or row["id"] in identifiers:
            raise ValueError("training row ids must be unique strings")
        identifiers.add(row["id"])
        names = row.get("tool_names") or list(available)
        if len(names) != len(set(names)) or any(name not in available for name in names):
            raise ValueError(f"{row['id']}: tool_names contains duplicates or unknown tools")
        if not isinstance(row.get("request"), str):
            raise ValueError(f"{row['id']}: request must be text")
        validate_history(row, names, available)
        target = row.get("target", {})
        if target.get("kind") == "tool":
            if target.get("name") not in names or not isinstance(target.get("arguments"), dict):
                raise ValueError(f"{row['id']}: target tool must be visible with object arguments")
            jsonschema.validate(target["arguments"], available[target["name"]]["function"]["parameters"])
        elif target.get("kind") != "words" or not isinstance(target.get("content"), str):
            raise ValueError(f"{row['id']}: target must be tool or words")
        row["tool_names"] = names
    # Post-tool completions teach result consumption, not ordinary no-tool behavior.
    plain = sum(row["target"]["kind"] == "words" and not row.get("history")
                for row in dataset["rows"])
    if plain * 4 < len(dataset["rows"]):
        raise ValueError("native tool SFT requires at least 25% plain-answer rows")
    return dataset, dataset["rows"]


def stable_tools(envelope: dict, names: list[str]) -> list[dict]:
    selected = set(names)
    return [tool for tool in envelope["tools"] if tool["function"]["name"] in selected]


def interleaved(rows: list[dict], seed: int) -> list[dict]:
    """Spread each group's original quota across the epoch without oversampling.

    See research/calculator-verified-training.md. Round-robin exhaustion leaves
    a task-only tail when retention groups are smaller than the new task.
    """
    groups = defaultdict(list)
    for row in rows:
        groups[row["group"]].append(row)
    rng = random.Random(seed)
    scheduled = []
    for values in groups.values():
        rng.shuffle(values)
        for index, row in enumerate(values):
            scheduled.append(((index + 0.5) / len(values), rng.random(), row))
    scheduled.sort(key=lambda item: item[:2])
    return [row for _, _, row in scheduled]


def toolset_groups(rows: list[dict]) -> list[list[dict]]:
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row["tool_names"])].append(row)
    return [groups[key] for key in sorted(groups)]


def training_profile(model, metadata: dict, *, last_k: int = 1) -> dict:
    """Select a correct feature/tail path from model capabilities.

    Recurrent models may expose a reusable prefix cache.  Selecting only target
    positions is valid when the trainable tail is tokenwise.  Ordinary decoder
    blocks keep the full sequence because their final attention still needs the
    prompt states.
    """
    architecture = str(metadata.get("general.architecture", "unknown"))
    file_type = int(metadata.get("general.file_type", -1))
    if file_type not in FULL_PRECISION_GGUF_TYPES:
        raise ValueError(
            f"training requires an F16 or BF16 GGUF, got file type {file_type}"
        )
    validate_model(model, architecture)
    if last_k <= 0 or last_k > len(model.blk):
        raise ValueError(f"last_k must be between 1 and {len(model.blk)}")
    trainable_tail = model.blk[-last_k:]
    cached = all(hasattr(model, name) for name in ("prime", "suffix"))
    tokenwise = all(getattr(block, "block_type", None) == "mlp" for block in trainable_tail)
    return {
        "architecture": architecture,
        "precision": FULL_PRECISION_GGUF_TYPES[file_type],
        "feature_layout": "target_only" if cached and tokenwise else "full_sequence",
        "last_k": last_k,
    }


def full_sequence_features(model, frequencies, sequence: list[int], *, through: int):
    """Run the frozen model prefix for an ordinary decoder-only architecture."""
    from tinygrad import Tensor
    hidden = model.token_embd(Tensor([sequence])).float()
    for index in range(through + 1):
        hidden = block_forward(
            model.blk[index], hidden, frequencies, retain_graph=False
        ).realize()
    return hidden


def prepare_group(chat, tokenizer, envelope: dict, rows: list[dict]) -> tuple[list[int], list[dict]]:
    tools = stable_tools(envelope, rows[0]["tool_names"])
    sentinel = "DAYCARE_NATIVE_TOOL_REQUEST_BOUNDARY"
    messages = [dict(message) for message in envelope["messages"]]
    messages[-1]["content"] = sentinel
    skeleton = chat.render(messages, tools, generation=True)
    if skeleton.count(sentinel) != 1:
        raise ValueError("request sentinel is not unique in rendered envelope")
    before, after = skeleton.split(sentinel)
    ids_before, ids_after = tokenizer.encode(before), tokenizer.encode(after)
    prepared = []
    for row in rows:
        messages = [dict(message) for message in envelope["messages"]]
        messages[-1]["content"] = row["request"]
        history = row.get("history", [])
        if history:
            prompt_text = chat.render(messages + history, tools, generation=True)
            if not prompt_text.startswith(before + row["request"]):
                raise ValueError(f"{row['id']}: history changed the request prefix")
            prompt = ids_before + tokenizer.encode(prompt_text[len(before):])
            if tokenizer.decode(prompt) != prompt_text:
                raise ValueError(f"{row['id']}: history-boundary token composition changed text")
            whole = chat.render(messages + history + [target_message(row["target"])], tools,
                                generation=False, target=True)
            if not whole.startswith(prompt_text):
                raise ValueError(f"{row['id']}: completed history changed generation prefix")
            completion = tokenizer.encode(whole[len(prompt_text):])
            if not completion or not any(tokenizer.is_end(token) for token in completion):
                raise ValueError(f"{row['id']}: target lacks an end-of-turn token")
        else:
            prompt_text = before + row["request"] + after
            prompt = ids_before + tokenizer.encode(row["request"]) + ids_after
            if tokenizer.decode(prompt) != prompt_text:
                raise ValueError(f"{row['id']}: request-boundary token composition changed text")
            whole = chat.render(messages + [target_message(row["target"])], tools,
                                generation=False, target=True)
            if not whole.startswith(prompt_text):
                raise ValueError(f"{row['id']}: completed conversation changed generation prefix")
            completion = tokenizer.encode(whole[len(prompt_text):])
            if not completion or not any(tokenizer.is_end(token) for token in completion):
                raise ValueError(f"{row['id']}: target lacks an end-of-turn token")
        prepared.append({**row, "prompt_ids": prompt, "completion_ids": completion})
    common = prepared[0]["prompt_ids"] + prepared[0]["completion_ids"]
    for row in prepared[1:]:
        sequence = row["prompt_ids"] + row["completion_ids"]
        stop = next((i for i, pair in enumerate(zip(common, sequence)) if pair[0] != pair[1]),
                    min(len(common), len(sequence)))
        common = common[:stop]
    if not rows[0].get("history") and prepared[0]["prompt_ids"] != tokenizer.encode(
            before + rows[0]["request"] + after):
        raise ValueError("fast request composition differs from full native tokenization")
    return common, prepared


def load_adapter(path: Path, adapters) -> str:
    saved = np.load(path)
    expected = {f"{index}_{name}" for index in range(len(adapters)) for name in ("A", "B")}
    if set(saved.files) != expected:
        raise ValueError("initial adapter tensor set differs from current target map")
    from tinygrad import Tensor
    for index, adapter in enumerate(adapters):
        for name in ("A", "B"):
            tensor, value = getattr(adapter, name), saved[f"{index}_{name}"]
            if tuple(value.shape) != tuple(tensor.shape):
                raise ValueError("initial adapter tensor shape differs from current target")
            tensor.assign(Tensor(value, device=tensor.device)).realize()
    return file_sha256(path)


def run(args):
    from daycare.model.decoder_forward import load
    from daycare.nursery.lora import apply_lora, freeze_model, lora_params, target_map
    from tinygrad import Tensor
    from tinygrad.nn.optim import Adam

    revision = source_revision()
    envelope = json.loads(args.envelope.read_text())
    dataset, rows = load_dataset(args.dataset, envelope)
    if Path(dataset["envelope"]).resolve() != args.envelope.resolve():
        raise ValueError("dataset envelope path differs from selected envelope")
    started = time.time()
    model, tokenizer, frequencies, metadata = load(args.model, max_context=args.max_context)
    profile = training_profile(model, metadata, last_k=args.last_k)
    chat = NativeToolChat(metadata["tokenizer.chat_template"], tokenizer)
    first_train_layer = len(model.blk) - args.last_k
    frozen_through = first_train_layer - 1
    features = args.output / "features"
    features.mkdir(parents=True, exist_ok=True)
    records, prepared_rows = [], []
    for group_index, group in enumerate(toolset_groups(rows)):
        common, prepared = prepare_group(chat, tokenizer, envelope, group)
        print(f"toolset {group_index + 1}: {len(group)} rows, {len(common)} common tokens, "
              f"layout={profile['feature_layout']}", flush=True)
        missing = any(not (features / f"{row['id']}.npz").exists() for row in prepared)
        caches = (
            model.prime(common, through=frozen_through)
            if missing and profile["feature_layout"] == "target_only" else None
        )
        for row in prepared:
            path = features / f"{row['id']}.npz"
            sequence = row["prompt_ids"] + row["completion_ids"]
            if not path.exists():
                if profile["feature_layout"] == "target_only":
                    hidden = model.suffix(
                        sequence[len(common):], caches, through=frozen_through
                    )
                    start = len(row["prompt_ids"]) - len(common) - 1
                    hidden = hidden[0, start:start + len(row["completion_ids"])].realize()
                    target_start = 0
                else:
                    hidden = full_sequence_features(
                        model, frequencies, sequence, through=frozen_through
                    )[0]
                    target_start = len(row["prompt_ids"]) - 1
                np.savez(
                    path, hidden=hidden.numpy().astype(np.float16),
                    targets=np.asarray(row["completion_ids"], dtype=np.int32),
                    target_start=np.asarray(target_start, dtype=np.int32),
                    layout=np.asarray(profile["feature_layout"]),
                )
            records.append({"id": row["id"], "sha256": file_sha256(path),
                            "tokens": len(row["completion_ids"])})
            prepared_rows.append(row)
        del caches
    write_json(args.output / "features.json", records)

    Tensor.manual_seed(dataset["seed"])
    adapters = apply_lora(model, r=args.rank, alpha=args.alpha, last_k=args.last_k)
    initial_sha = load_adapter(args.init_adapter, adapters) if args.init_adapter else None
    freeze_model(model)
    params = lora_params(adapters)
    for parameter in params:
        parameter.is_param_(True)
    optimizer = Adam(params, lr=args.lr)
    losses = []
    for epoch in range(args.epochs):
        for row in interleaved(prepared_rows, dataset["seed"] + epoch):
            saved = np.load(features / f"{row['id']}.npz")
            with Tensor.train():
                optimizer.zero_grad()
                inputs = Tensor(saved["hidden"]).unsqueeze(0).float()
                if str(saved["layout"]) == "target_only":
                    hidden = inputs
                    for layer in range(first_train_layer, len(model.blk)):
                        hidden = model.blk[layer](hidden)
                else:
                    hidden = inputs
                    for layer in range(first_train_layer, len(model.blk)):
                        hidden = block_forward(model.blk[layer], hidden, frequencies)
                    start = int(saved["target_start"])
                    hidden = hidden[:, start:start + len(saved["targets"])]
                logits = model.output(model.output_norm(hidden))[0]
                loss = logits.sparse_categorical_crossentropy(Tensor(saved["targets"]), reduction="mean")
                loss.backward()
                norm = sum(parameter.grad.square().sum() for parameter in params).sqrt()
                value, grad_norm = float(loss.item()), float(norm.item())
                if not np.isfinite(value + grad_norm):
                    raise ValueError("nonfinite training value")
                if grad_norm > 1.0:
                    for parameter in params:
                        parameter.grad = parameter.grad / grad_norm
                optimizer.step()
            losses.append({"step": len(losses) + 1, "epoch": epoch, "id": row["id"],
                           "group": row["group"], "loss": value, "grad_norm": grad_norm})
            write_json(args.output / "progress.json", {"complete": False, "losses": losses})
    adapter_path = args.output / "adapter.npz"
    np.savez(adapter_path, **{f"{index}_{name}": getattr(adapter, name).numpy().copy()
                              for index, adapter in enumerate(adapters) for name in ("A", "B")})
    result = {"schema": SCHEMA, "complete": True, "daycare_revision": revision,
              "runner_sha256": file_sha256(Path(__file__)), "dataset_sha256": file_sha256(args.dataset),
              "envelope_sha256": file_sha256(args.envelope), "model_sha256": file_sha256(args.model),
              "initial_adapter_sha256": initial_sha, "adapter_sha256": file_sha256(adapter_path),
              "model_profile": profile,
              "examples": len(rows), "toolsets": len(toolset_groups(rows)), "epochs": args.epochs,
              "rank": args.rank, "alpha": args.alpha, "lr": args.lr, "last_k": args.last_k,
              "target_map": target_map(adapters),
              "seconds": time.time() - started, "losses": losses}
    write_json(args.output / "run.json", result)
    write_json(args.output / "progress.json", result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--envelope", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--init-adapter", type=Path)
    parser.add_argument("--rank", type=int, default=4)
    parser.add_argument("--alpha", type=float, default=8)
    parser.add_argument("--last-k", type=int, default=1)
    parser.add_argument("--lr", type=float, default=5e-5)
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--max-context", type=int, default=12288)
    args = parser.parse_args()
    if min(args.rank, args.alpha, args.last_k, args.lr, args.epochs, args.max_context) <= 0:
        parser.error("training parameters must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    result = run(args)
    print(json.dumps({key: result[key] for key in ("adapter_sha256", "examples", "toolsets", "seconds")},
                     indent=2))


if __name__ == "__main__":
    main()
