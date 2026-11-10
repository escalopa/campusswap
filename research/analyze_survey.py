"""Summarize CampusSwap survey and screener answers for the research report.

Export the tab from the "CampusSwap — Research data" spreadsheet (File → Download → CSV), then:

  python research/analyze_survey.py survey  "Survey responses.csv"  --out research/results
  python research/analyze_survey.py screener "Screener responses.csv"

`survey` writes results/summary.md (every question with counts and %) and one bar chart per question
(results/q*.png, needs matplotlib). `screener` prints who matches the recruiting criteria and the mix.
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from collections import Counter
from pathlib import Path

GREEN = "#1E7B5C"
INK = "#14161A"
MUTED = "#5C6370"
GRID = "#D5D8DD"


def read(path: str) -> tuple[list[str], list[dict[str, str]]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def split_multi(value: str) -> list[str]:
    # Google Forms joins checkbox answers with ", ". Our option labels contain no ", ".
    return [v.strip() for v in value.split(", ") if v.strip()]


def qnum(title: str) -> str:
    m = re.match(r"\s*(\d+)\.", title)
    return m.group(1) if m else title[:20]


def kind_of(title: str, values: list[str]) -> str:
    if "[" in title and title.endswith("]"):
        return "grid"
    nonempty = [v for v in values if v]
    if nonempty and all(v.isdigit() for v in nonempty) and title[:3] in ("7. ", "12."):
        return "scale"
    if title.startswith("13."):
        return "text"
    if any(", " in v for v in nonempty) or title[:3] in ("3. ", "4. ", "5. ", "6. ", "8. ") or title.startswith("10."):
        return "multi"
    return "single"


def bar_chart(title: str, counts: list[tuple[str, int]], n: int, path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    labels = [c[0] for c in counts][::-1]
    pct = [100 * c[1] / n for c in counts][::-1]
    fig, ax = plt.subplots(figsize=(7, 0.45 * len(labels) + 1.1), dpi=200)
    bars = ax.barh(labels, pct, color=GREEN, height=0.55)
    for b, p, (_, c) in zip(bars, pct, counts[::-1]):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2, f"{p:.0f}% ({c})", va="center",
                fontsize=8, color=INK)
    ax.set_xlim(0, max(pct + [1]) * 1.25)
    ax.set_title(title, loc="left", fontsize=10, color=INK, wrap=True)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.xaxis.set_visible(False)
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(GRID)
    fig.text(0.01, 0.01, f"n = {n} respondents", fontsize=7, color=MUTED)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def survey(path: str, out: Path) -> None:
    fields, rows = read(path)
    q1 = next((f for f in fields if f.startswith("1.")), None)
    rows = [r for r in rows if not q1 or r.get(q1) == "Yes"]  # dorm residents only
    n = len(rows)
    out.mkdir(parents=True, exist_ok=True)
    lines = [f"# Survey summary\n\nDorm residents who answered: **{n}**\n"]
    grid: dict[str, list[tuple[str, float]]] = {}
    for f in fields:
        if f in ("Timestamp", q1) or not f.strip():
            continue
        values = [r.get(f, "").strip() for r in rows]
        k = kind_of(f, values)
        if k == "grid":
            base, row = f[: f.index("[")].strip(), f[f.index("[") + 1 : -1]
            ranks = [int(v) for v in values if v.isdigit()]
            if ranks:
                grid.setdefault(base, []).append((row, statistics.mean(ranks)))
            continue
        lines.append(f"## {f}\n")
        if k == "text":
            answers = [v for v in values if v]
            lines += [f"- {a}" for a in answers] or ["*(no answers)*"]
            lines.append("")
            continue
        if k == "scale":
            nums = [int(v) for v in values if v.isdigit()]
            if nums:
                lines.append(f"Average **{statistics.mean(nums):.1f}** / 5, median {statistics.median(nums):g}\n")
            counts = sorted(Counter(str(x) for x in nums).items())
        else:
            c = Counter(x for v in values for x in (split_multi(v) if k == "multi" else [v]) if x)
            counts = c.most_common()
        lines += ["| Answer | Count | % |", "|---|---:|---:|"]
        lines += [f"| {a} | {c} | {100 * c / n:.0f}% |" for a, c in counts] if n else []
        lines.append("")
        bar_chart(f, counts, max(n, 1), out / f"q{qnum(f)}.png")
    for base, ranked in grid.items():
        lines += [f"## {base}\n", "Lower average rank = more important.\n", "| Factor | Average rank |", "|---|---:|"]
        lines += [f"| {r} | {m:.1f} |" for r, m in sorted(ranked, key=lambda x: x[1])]
        lines.append("")
    (out / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out / 'summary.md'} ({n} respondents)")


def screener(path: str) -> None:
    fields, rows = read(path)
    col = lambda prefix: next((f for f in fields if f.startswith(prefix)), None)  # noqa: E731
    lives, avail, done = col("Do you currently live"), col("Are you available"), col("In the last 12 months")
    origin, name, tg = col("Are you a local"), col("Your first name"), col("Your Telegram")
    ok = [r for r in rows if r.get(lives) == "Yes" and r.get(avail) == "Yes"
          and "None of these" not in r.get(done, "")]
    print(f"{len(ok)} of {len(rows)} respondents match (dorm resident, available, has exchanged items)\n")
    for r in ok:
        roles = split_multi(r.get(done, ""))
        gives = any(x in roles for x in ("Sold an item", "Gave an item away for free"))
        gets = any(x in roles for x in ("Bought a used item", "Received an item for free"))
        role = "both" if gives and gets else "gives" if gives else "gets"
        print(f"- {r.get(name, '?'):<14} {r.get(tg, ''):<22} {r.get(origin, ''):<14} {role}")
    print("\nAim for: 2+ givers, 2+ getters, 1+ international, 1+ local, mixed years.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("survey")
    s.add_argument("csv")
    s.add_argument("--out", default="research/results", type=Path)
    sc = sub.add_parser("screener")
    sc.add_argument("csv")
    a = p.parse_args()
    survey(a.csv, a.out) if a.cmd == "survey" else screener(a.csv)


if __name__ == "__main__":
    main()
