#!/opt/homebrew/bin/python3.12
"""Turn one run's result files into Markdown: one page per model and a summary.

    python3.12 bc-arithmetic/report.py results/2026-09-19
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def shown(value) -> str:
    if value is None:
        return "no number"
    return str(int(value)) if float(value).is_integer() else str(value)


def grouped(rows):
    """The attempts of each question, in question order."""
    order, groups = [], {}
    for row in rows:
        if row["question"] not in groups:
            order.append(row["question"])
        groups.setdefault(row["question"], []).append(row)
    return [groups[question] for question in order]


def score(rows) -> str:
    return f"{sum(r['right'] for r in rows)} of {len(rows)}"


def percent(rows) -> str:
    return f"{100 * sum(r['right'] for r in rows) / max(1, len(rows)):.0f}%"


def cell(attempts) -> str:
    answers = ", ".join(shown(a["got"]) for a in attempts)
    return f"{sum(a['right'] for a in attempts)}/{len(attempts)} ({answers})"


def model_page(data) -> str:
    rows = data["results"]
    head, tool = [r for r in rows if not r["tool"]], [r for r in rows if r["tool"]]
    repeats = data.get("repeats", 1)
    lines = [f"# {data['model']}", "",
             f"Engine `{data['engine']}`, thinking off, GameTerm's sampling "
             f"(temperature {data['sampling']['temperature']}, top_p {data['sampling']['top_p']}). "
             f"{data['questions']} questions, each asked {repeats} time(s) per condition.", "",
             "| Condition | Right | Share | Seconds per question |", "|---|---|---|---|"]
    for name, part in (("In its head", head), ("With bc", tool)):
        seconds = sum(r["seconds"] for r in part) / max(1, len(part))
        lines.append(f"| {name} | {score(part)} | {percent(part)} | {seconds:.1f} |")
    called = sum(1 for r in tool if r["calls"])
    commands = [c for r in tool for c in r["calls"]]
    refused = sum(1 for c in commands if c["output"].startswith("refused"))
    errors = sum(1 for c in commands if "error" in c["output"].lower())
    lines += ["", f"With the tool offered it called bc in {called} of {len(tool)} attempts, {len(commands)} commands in all. "
                  f"{refused} were refused by the filter (not a plain bc command) and {errors} ended in a bc error.", "",
              "## Every question", "",
              "Each cell: attempts that were right, then the answers given.", "",
              "| Level | Question | Expected | In its head | With bc | A bc command it wrote |", "|---|---|---|---|---|---|"]
    for a, b in zip(grouped(head), grouped(tool)):
        first = next((c for attempt in b for c in attempt["calls"]), None)
        command = f"`{first['command']}` → `{first['output'][:40]}`".replace("|", "¦") if first else "none"
        lines.append(f"| {a[0]['level']} | {a[0]['question']} | {shown(a[0]['want'])} | {cell(a)} | {cell(b)} | {command} |")
    return "\n".join(lines) + "\n"


def main():
    run = (HERE / sys.argv[1]) if not Path(sys.argv[1]).is_absolute() else Path(sys.argv[1])
    pages = [json.loads(path.read_text()) for path in sorted(run.glob("*.json"))]
    levels = sorted({r["level"] for page in pages for r in page["results"]})
    repeats = max(page.get("repeats", 1) for page in pages)
    summary = [f"# bc arithmetic, run {run.name}", "",
               f"Each question asked {repeats} time(s) per condition. Share of right answers overall, then by "
               "difficulty level (in its head → with bc).", "",
               "| Model | In its head | With bc | Seconds (head → bc) | " + " | ".join(f"L{level}" for level in levels) + " |",
               "|---|---|---|---|" + "---|" * len(levels)]
    for page in pages:
        (run / f"{page['model']}.md").write_text(model_page(page))
        rows = page["results"]
        head, tool = [r for r in rows if not r["tool"]], [r for r in rows if r["tool"]]
        cells = []
        for level in levels:
            h = [r for r in head if r["level"] == level]
            t = [r for r in tool if r["level"] == level]
            cells.append(f"{percent(h)} → {percent(t)}")
        seconds = lambda part: sum(r["seconds"] for r in part) / max(1, len(part))
        summary.append(f"| [{page['model']}]({page['model']}.md) | {score(head)} ({percent(head)}) | "
                       f"{score(tool)} ({percent(tool)}) | {seconds(head):.1f} → {seconds(tool):.1f} | " + " | ".join(cells) + " |")
    (run / "README.md").write_text("\n".join(summary) + "\n")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
