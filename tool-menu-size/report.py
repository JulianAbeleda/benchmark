#!/opt/homebrew/bin/python3.12
"""Score one run twice: strictly (only the final tool counts) and fairly (a
lookup before the action is a sensible first step, not a wrong pick).

    python3.12 tool-menu-size/report.py results/2026-09-20
"""
import collections, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# What a model may reasonably call first, before the tool that does the job.
LOOKUPS = {"app_open": {"app_list", "app_status", "role_resolve"},
           "media_play": {"role_resolve", "app_status", "media_status", "app_list", "app_open"},
           "window_tile": {"window_list", "window_list_managed", "app_list", "role_resolve", "window_workspace"}}


def kind(row) -> str:
    if row["ok"]:
        return "right"
    first = (row["called"] or [None])[0]
    if first is None:
        return "no tool call"
    if not row["right_tools"]:
        return "needless call"
    gold = next((tool for tool in row["right_tools"] if tool in LOOKUPS), None)
    return "lookup first" if gold and first in LOOKUPS[gold] else "wrong tool"


def main():
    run = HERE / sys.argv[1]
    lines = [f"# Tool menu size, run {run.name}", "",
             "Attempts whose first tool call was right. *Strict*: only the tool that does the job counts. "
             "*Fair*: a lookup first (listing apps or windows before acting on them) counts too.", "",
             "| Model | Tools shown | Prompt tokens | Strict | Fair | Wrong tool | No tool call | Needless call |",
             "|---|---|---|---|---|---|---|---|"]
    for path in sorted(run.glob("*.json")):
        data = json.loads(path.read_text())
        for size in sorted({r["size"] for r in data["results"]}):
            part = [r for r in data["results"] if r["size"] == size]
            c = collections.Counter(kind(r) for r in part)
            lines.append(f"| {data['model']} | {size} | {part[0]['prompt_tokens']} | {c['right']} of {len(part)} | "
                         f"{c['right'] + c['lookup first']} of {len(part)} | {c['wrong tool']} | {c['no tool call']} | {c['needless call']} |")
    (run / "README.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
