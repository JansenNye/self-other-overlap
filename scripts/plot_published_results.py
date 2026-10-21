"""Plot archived Gemma-4-12B adapter-subset counts; no model or GPU required."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    root = Path(__file__).resolve().parents[1]
    rows = json.loads((root / "published/study2-summaries.json").read_text())
    run = "bisect-gemma4-12b-L24-20260924T220341Z"
    conditions = [("base", "Base"), ("adapter-seed0", "Full adapter"),
                  ("below-v", "All values below L24"), ("band", "Value band L19–23")]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for offset, orientation, color in [(-.18, "orig", "#315b8a"), (.18, "mirrored", "#c76c3d")]:
        rates = []
        for condition, _ in conditions:
            name = f"{condition}_{orientation}_main_room_only_summary.json"
            matches = [r for r in rows if r["run"] == run and r["file"] == name]
            if len(matches) != 1:
                raise ValueError(f"Expected exactly one archived result: {run}/{name}")
            row = matches[0]
            rates.append(100 * row["counts"]["deceptive"] / row["n"])
        ax.bar([i + offset for i in range(len(conditions))], rates, width=.36,
               label="Original" if orientation == "orig" else "Mirrored", color=color)
    ax.set_xticks(range(len(conditions)), [label for _, label in conditions])
    ax.set_ylabel("Deceptive responses (%)")
    ax.set_ylim(0, 105)
    ax.set_title("Gemma-4-12B: adapter subsets, 250 prompts per condition")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    out = root / "outputs"
    out.mkdir(exist_ok=True)
    for extension in ("png", "svg"):
        fig.savefig(out / f"adapter-subsets.{extension}", dpi=180)
    plt.close(fig)
    print(out / "adapter-subsets.png")


if __name__ == "__main__":
    main()
