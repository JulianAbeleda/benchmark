#!/opt/homebrew/bin/python3.12
"""How many tools can a small local model see before it starts picking the wrong one?

The same requests are asked with 6, 12, 20 and 35 tools on the menu. The six
"gold" tools are always there; each larger menu adds the most similar tools
first, the hardest distractors. Scored: is the model's first tool call the
right tool (or no call, for a request that needs none)?

The tool definitions are a real application's, read from a local file that is
not in this repository (`--tools`, default `tools.local.json`): a JSON list in
the OpenAI `tools` format. The menus below name tools from that file.

Within one menu size every request sends the identical tool list, so the
engine's prompt cache holds it and a request costs little more than its
question.
"""
import argparse, datetime, json, os, random, subprocess, time, urllib.request
from pathlib import Path

ROOT = Path.home() / "Library/Application Support/Arkey"
PORT = 8097
HERE = Path(__file__).resolve().parent

GOLD = ["calculate", "app_open", "media_play", "mcp__provider.search__web_search", "window_tile", "read_file"]
MENUS = {
    6: [],
    12: ["app_status", "app_list", "media_status", "window_list", "write_file", "bash"],
    20: ["terminal_open", "terminal_send", "terminal_read", "window_place", "window_focus", "role_resolve",
         "update_plan", "mcp__provider.spotify__search"],
    35: None,  # every tool in the file
}
# (request, the tools that count as right; an empty set means no tool call is right)
REQUESTS = [
    ("What is 487 times 36?", {"calculate"}),
    ("What is 15 percent of 80?", {"calculate"}),
    ("What is the square root of 2, times 100?", {"calculate"}),
    ("Open Safari.", {"app_open"}),
    ("Can you launch the Notes app?", {"app_open"}),
    ("Open the Calculator app for me.", {"app_open"}),
    ("Play Mr. Suave by Parokya ni Edgar.", {"media_play", "mcp__provider.spotify__search"}),
    ("Put on the song Stronger by Kanye West.", {"media_play", "mcp__provider.spotify__search"}),
    ("Play some Daft Punk.", {"media_play", "mcp__provider.spotify__search"}),
    ("Search the web for the latest stable Rust release.", {"mcp__provider.search__web_search"}),
    ("Look up today's top news headlines online.", {"mcp__provider.search__web_search"}),
    ("Search online for the weather in Manila right now.", {"mcp__provider.search__web_search"}),
    ("Tile Safari and Notes side by side.", {"window_tile", "window_place"}),
    ("Put Safari on the left half of the screen and Terminal on the right half.", {"window_tile", "window_place"}),
    ("Arrange my two open windows next to each other.", {"window_tile", "window_place"}),
    ("Read the file notes.txt in my workspace and tell me what it says.", {"read_file"}),
    ("Show me the contents of README.md.", {"read_file"}),
    ("What is written in todo.txt?", {"read_file"}),
    ("Hi, how are you today?", set()),
    ("Tell me a short joke.", set()),
    ("What is the capital of France?", set()),
]
SYSTEM = "You are a desktop assistant on a Mac. When a tool fits the request, call it. When none is needed, just answer."
SAMPLING = {"temperature": 0.7, "top_p": 0.81, "repeat_penalty": 1.1, "presence_penalty": 1.4,
            "chat_template_kwargs": {"enable_thinking": False}, "max_tokens": 300}


def menu(tools, size):
    by_name = {t["function"]["name"]: t for t in tools}
    names = list(GOLD)
    for step in sorted(MENUS):
        if step > size:
            break
        extra = MENUS[step]
        names += [n for n in (by_name if extra is None else extra) if n not in names]
    missing = [n for n in names if n not in by_name]
    if missing:
        raise SystemExit(f"the tools file has no {missing}")
    random.Random(size).shuffle(names)  # a fixed order per size: no tool owes its score to coming first
    return [by_name[n] for n in names]


def chat(question, tools):
    body = dict(SAMPLING, model="m", stream=False, tools=tools, tool_choice="auto",
                messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}])
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/chat/completions",
                                     json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(request, timeout=600))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("models", nargs="*")
    parser.add_argument("--tools", type=Path, default=HERE / "tools.local.json")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--sizes", type=int, nargs="*", default=sorted(MENUS))
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--run", default=datetime.date.today().isoformat())
    arguments = parser.parse_args()
    tools = json.loads(arguments.tools.read_text())
    engine_path = sorted((arguments.root / "engines/llama").glob("*/llama-server"))[-1]
    models = arguments.models or sorted(p.parent.name for p in (arguments.root / "models").glob("*/model.gguf"))
    out = HERE / "results" / arguments.run
    out.mkdir(parents=True, exist_ok=True)
    for model in models:
        engine = subprocess.Popen(
            [str(engine_path), "-m", str(arguments.root / "models" / model / "model.gguf"), "--alias", "m", "--host", "127.0.0.1",
             "--port", str(PORT), "--ctx-size", "16384", "-fa", "on", "--cache-type-k", "q8_0", "--cache-type-v", "q8_0",
             "--no-webui", "--reasoning", "off", "--gpu-layers", "all", "--jinja"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ, GGML_METAL_NO_RESIDENCY="1"))
        rows = []
        try:
            for _ in range(180):
                try:
                    if b"ok" in urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1).read():
                        break
                except OSError:
                    time.sleep(1)
            for size in arguments.sizes:
                shown = menu(tools, size)
                for attempt in range(arguments.repeats):
                    for question, right in REQUESTS:
                        started = time.monotonic()
                        try:
                            reply = chat(question, shown)
                            message = reply["choices"][0]["message"]
                            called = [c["function"]["name"] for c in message.get("tool_calls") or []]
                            prompt_tokens, error = reply.get("usage", {}).get("prompt_tokens"), None
                        except Exception as problem:
                            called, prompt_tokens, error = [], None, str(problem)[:160]
                        first = called[0] if called else None
                        ok = (first in right) if right else (first is None)
                        rows.append({"size": size, "attempt": attempt + 1, "question": question, "right_tools": sorted(right),
                                     "called": called, "ok": bool(ok) and error is None, "prompt_tokens": prompt_tokens,
                                     "seconds": round(time.monotonic() - started, 1), "error": error})
                part = [r for r in rows if r["size"] == size]
                print(json.dumps({"model": model, "tools_shown": size, "right": sum(r["ok"] for r in part), "of": len(part),
                                  "prompt_tokens": part[0]["prompt_tokens"],
                                  "seconds_each": round(sum(r["seconds"] for r in part) / len(part), 1)}), flush=True)
        finally:
            engine.terminate()
            try:
                engine.wait(timeout=20)
            except subprocess.TimeoutExpired:
                engine.kill()
        (out / f"{model}.json").write_text(json.dumps(
            {"model": model, "engine": engine_path.parent.name, "sampling": SAMPLING, "system": SYSTEM,
             "menus": {str(size): [t["function"]["name"] for t in menu(tools, size)] for size in arguments.sizes},
             "repeats": arguments.repeats, "results": rows}, indent=1) + "\n")


if __name__ == "__main__":
    main()
