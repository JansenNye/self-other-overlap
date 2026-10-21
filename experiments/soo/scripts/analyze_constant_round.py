"""Exploratory readout for a constant-replacement round (docs/plans/README.md).

Usage: python analyze_constant_round.py OUTPUT_DIR   (the job's output/ directory)
Reads output/eval/<condition>_<orient>_<scenario>_<suffix>_summary.json and .jsonl,
writes output/analysis.json and output/analysis.md. Exploratory; no honesty claim.
"""

import json
from pathlib import Path
import sys

CONDITIONS = ("base", "adapter-seed0", "replace-adapter-s0", "replace-adapter-s1", "replace-adapter-s2",
              "replace-base-mean", "replace-zero", "replace-random-s0", "replace-random-s1", "replace-random-s2",
              "replace-adapter-s0-all", "replace-base-mean-all")
from analysis_common import ORIENTS, SCENARIOS, REFERENCE, TOL, DAMAGE_OTHER, PERSP_OK, PERSP_DAMAGE, load, wilson, fmt_rates


def main():
    out = Path(sys.argv[1])
    runs = load(out, include_subset=False)
    missing = [f"{c}/{o}/{s}" for c in CONDITIONS for o in ORIENTS for s in SCENARIOS if s not in runs.get(c, {}).get(o, {})]
    verdicts = {}
    ref = runs.get(REFERENCE, {})
    for cond in CONDITIONS:
        if cond in ("base", REFERENCE) or cond not in runs:
            continue
        checks, ok, damage = {}, True, False
        for o in ORIENTS:
            r = runs[cond].get(o, {}); rr = ref.get(o, {})
            if "main" not in r or "main" not in rr or "perspectives" not in r:
                ok = False; checks[o] = "incomplete"; continue
            d, dref = r["main"]["rates"]["deceptive"], rr["main"]["rates"]["deceptive"]
            oth = r["main"]["rates"]["refusal"] + r["main"]["rates"]["other"]
            othref = rr["main"]["rates"]["refusal"] + rr["main"]["rates"]["other"]
            persp = r["perspectives"]["rates"]["honest"]
            c = {"deceptive": d, "deceptive_ref": dref, "refusal_other": oth, "refusal_other_ref": othref, "perspectives_correct": persp,
                 "within_tol": abs(d - dref) <= TOL, "other_ok": oth <= othref + TOL, "persp_ok": persp >= PERSP_OK}
            checks[o] = c
            ok = ok and c["within_tol"] and c["other_ok"] and c["persp_ok"]
            damage = damage or oth > DAMAGE_OTHER or persp < PERSP_DAMAGE
        verdicts[cond] = {"reproduces_adapter": ok, "damage": damage, "checks": checks}

    lines = ["# Constant-replacement round analysis (auto-generated, exploratory)", "",
             f"Missing runs: {', '.join(missing) if missing else 'none'}", ""]
    for o in ORIENTS:
        lines += [f"## {o}: classifier rates (honest / deceptive / refusal / other), deceptive 95% Wilson CI on main", "",
                  "| Condition | main H/D/R/O | main D CI | treasure_hunt H/D/R/O | perspectives correct |", "|---|---|---|---|---:|"]
        for cond in CONDITIONS:
            r = runs.get(cond, {}).get(o, {})
            ci = "—"
            if "main" in r:
                lo, hi = wilson(r["main"]["counts"]["deceptive"], r["main"]["n"]); ci = f"[{lo:.2f}, {hi:.2f}]"
            persp = f"{r['perspectives']['rates']['honest']:.2f}" if "perspectives" in r else "—"
            lines.append(f"| {cond} | {fmt_rates(r, 'main')} | {ci} | {fmt_rates(r, 'treasure_hunt')} | {persp} |")
        lines.append("")
    lines += ["## Verdicts against the published exploratory rule", ""]
    for cond, v in verdicts.items():
        lines.append(f"- {cond}: reproduces adapter {v['reproduces_adapter']}, damage {v['damage']}")
    lines += ["", "## First five main-scenario responses (orig)", ""]
    for cond in CONDITIONS:
        r = runs.get(cond, {}).get("orig", {}).get("main")
        if not r or "samples" not in r:
            continue
        lines.append(f"### {cond}")
        for s in r["samples"]:
            txt = s["response"].replace("\n", " ")[:160]
            lines.append(f"- [{s['label']}] {txt}")
        lines.append("")
    consts = out / "constants.json"
    if consts.exists():
        lines += ["## Constant statistics (make_constants.py)", "", "```", consts.read_text().strip(), "```", ""]
    (out / "analysis.json").write_text(json.dumps({"note": "exploratory; rule in docs/plans/README.md", "missing": missing, "runs": runs, "verdicts": verdicts}, indent=2) + "\n")
    (out / "analysis.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
