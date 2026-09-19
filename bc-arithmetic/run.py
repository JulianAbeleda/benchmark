#!/opt/homebrew/bin/python3.12
"""How well do small local models use bc for arithmetic?

For each model under the Arkey root: start the engine the way GameTerm does
(thinking off, GameTerm's sampling), ask 16 questions of rising difficulty
twice: in its head, and with a `bash` tool and a hint to use bc. The tool
runs bc for real, and only bc: the command is parsed here, the expression is
checked, and bc gets it on stdin. No shell ever sees the model's text.
"""
import argparse, datetime, json, os, re, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path.home() / "Library/Application Support/Arkey"
ENGINE = ROOT / "engines/llama/llama-b10948/llama-server"
PORT = 8097
HERE = Path(__file__).resolve().parent

# (level, question, exact answer)
QUESTIONS = [
    (1, "What is 2 plus 2?", 4),
    (1, "What is 10 minus 4?", 6),
    (2, "What is 487 times 36?", 17532),
    (2, "What is 9126 divided by 18?", 507),
    (3, "What is 15 percent of 80?", 12),
    (3, "What is 19.99 times 3?", 59.97),
    (4, "What is (1499 times 12) divided by 7? Round to 2 decimals.", 2569.71),
    (4, "What is the average of 23, 47, 58, 91 and 106?", 65),
    (5, "What is 123456789 times 987654321?", 121932631112635269),
    (5, "What is 2 to the power of 40?", 1099511627776),
    (6, "A shirt costs 24.50. It is 20 percent off. Then 8 percent sales tax is added. "
        "What do 3 shirts cost in total? Round to 2 decimals.", 63.50),
    (6, "1000 dollars grows at 5 percent a year, compounded yearly, for 10 years. "
        "What is the final amount? Round to 2 decimals.", 1628.89),
    (7, "A right triangle has legs of 5 and 12. How long is the hypotenuse?", 13),
    (7, "What is the square root of 2, times 100? Round to 2 decimals.", 141.42),
    (8, "What is the remainder when 1000003 is divided by 97?", 30),
    (8, "What is 2 to the power of 0.5, times 10? Round to 3 decimals.", 14.142),
]

HEAD = ("You are a helpful assistant. Work the problem out and end your reply with a line "
        "of the form ANSWER: <number>, a plain number such as 1234.56, with no units and no commas.")
TOOL = ("You are a helpful assistant on a Mac. Do not do arithmetic in your head. For every "
        "calculation call the bash tool with a bc command, for example: echo \"(3+4)*2\" | bc -l . "
        "Read the result, then end your reply with a line of the form ANSWER: <number>, a plain "
        "number such as 1234.56, with no units and no commas.")
BASH = [{"type": "function", "function": {
    "name": "bash", "description": "Run one shell command on this Mac and return its output.",
    "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}}]
SAMPLING = {"temperature": 0.7, "top_p": 0.81, "repeat_penalty": 1.1, "presence_penalty": 1.4,
            "chat_template_kwargs": {"enable_thinking": False}, "max_tokens": 600}

FORMS = [r"""^\s*echo\s+(?:-e\s+)?(['"])(?P<e>.*)\1\s*\|\s*bc(?P<l>\s+-l)?\s*$""",
         r"""^\s*echo\s+(?P<e>[^|'"]+?)\s*\|\s*bc(?P<l>\s+-l)?\s*$""",
         r"""^\s*bc(?P<l>\s+-l)?\s*<<<\s*(['"])(?P<e>.*)\2\s*$"""]
SAFE = re.compile(r"^[0-9a-z+\-*/^().,%;=<> \n]*$")


def run_bc(command: str) -> str:
    """bc and nothing else. The expression reaches bc on stdin, never a shell."""
    for form in FORMS:
        match = re.match(form, command, re.S)
        if match:
            expression = match.group("e").replace("\\n", "\n")
            if not SAFE.match(expression):
                return "refused: only numbers, operators and bc function names are allowed"
            done = subprocess.run(["/usr/bin/bc"] + (["-l"] if match.group("l") else []),
                                  input=expression + "\n", capture_output=True, text=True, timeout=5)
            return (done.stdout + done.stderr).replace("\\\n", "").strip() or "(no output)"
    return "refused: only a bc command is allowed here, like: echo \"1+2\" | bc -l"


def chat(messages, tools=None):
    body = dict(SAMPLING, model="m", messages=messages, stream=False)
    if tools:
        body.update(tools=tools, tool_choice="auto")
    request = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/chat/completions",
                                     json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(request, timeout=300))["choices"][0]["message"]


def number_in(reply: str):
    text = reply.replace(",", "")
    tagged = re.findall(r"ANSWER:\s*\$?\s*(-?\d+(?:\.\d+)?)", text)
    found = tagged or re.findall(r"-?\d+(?:\.\d+)?", text)
    return float(found[-1]) if found else None


def right(got, want) -> bool:
    if got is None:
        return False
    if float(want).is_integer() and abs(want) > 1e9:
        return int(got) == int(want) or abs(got - want) / abs(want) < 1e-12
    return abs(got - want) <= max(0.006, abs(want) * 1e-6)


def ask(question, with_tool):
    messages = [{"role": "system", "content": TOOL if with_tool else HEAD}, {"role": "user", "content": question}]
    calls = []
    for _ in range(5):
        message = chat(messages, BASH if with_tool else None)
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            return message.get("content") or "", calls
        messages.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": tool_calls})
        for call in tool_calls:
            try:
                command = json.loads(call["function"]["arguments"]).get("command", "")
            except (ValueError, AttributeError):
                command = ""
            output = run_bc(command)
            calls.append({"command": command, "output": output[:120]})
            messages.append({"role": "tool", "tool_call_id": call.get("id", "0"), "content": output})
    return "", calls


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("models", nargs="*", help="model folders under <root>/models; default: every folder with a model.gguf")
    parser.add_argument("--root", type=Path, default=ROOT, help="the Arkey root (engines/ and models/)")
    parser.add_argument("--engine", type=Path, help="llama-server; default: the newest under <root>/engines/llama")
    parser.add_argument("--run", default=datetime.date.today().isoformat(), help="the run's folder name under results/")
    arguments = parser.parse_args()
    engine_path = arguments.engine or sorted((arguments.root / "engines/llama").glob("*/llama-server"))[-1]
    models = arguments.models or sorted(p.parent.name for p in (arguments.root / "models").glob("*/model.gguf"))
    out = HERE / "results" / arguments.run
    out.mkdir(parents=True, exist_ok=True)
    for model in models:
        results = []
        engine = subprocess.Popen(
            [str(engine_path), "-m", str(arguments.root / "models" / model / "model.gguf"), "--alias", "m", "--host", "127.0.0.1",
             "--port", str(PORT), "--ctx-size", "8192", "-fa", "on", "--cache-type-k", "q8_0", "--cache-type-v", "q8_0",
             "--no-webui", "--reasoning", "off", "--gpu-layers", "all", "--jinja"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ, GGML_METAL_NO_RESIDENCY="1"))
        try:
            for _ in range(180):
                try:
                    if b"ok" in urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1).read():
                        break
                except OSError:
                    time.sleep(1)
            for with_tool in (False, True):
                for level, question, want in QUESTIONS:
                    started = time.monotonic()
                    try:
                        reply, calls = ask(question, with_tool)
                        error = None
                    except Exception as problem:  # a model that cannot take tools is a result too
                        reply, calls, error = "", [], str(problem)[:160]
                    got = number_in(reply)
                    row = {"model": model, "tool": with_tool, "level": level, "question": question, "want": want,
                           "got": got, "right": right(got, want), "calls": calls,
                           "seconds": round(time.monotonic() - started, 1), "reply": reply[-300:], "error": error}
                    results.append(row)
                    print(json.dumps({k: row[k] for k in ("model", "tool", "level", "want", "got", "right", "seconds")}
                                     | {"n_calls": len(calls)}), flush=True)
        finally:
            engine.terminate()
            try:
                engine.wait(timeout=20)
            except subprocess.TimeoutExpired:
                engine.kill()
        (out / f"{model}.json").write_text(json.dumps(
            {"model": model, "engine": engine_path.parent.name, "sampling": SAMPLING, "questions": len(QUESTIONS),
             "results": results}, indent=1) + "\n")


if __name__ == "__main__":
    main()
