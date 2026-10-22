# Recovered first-study records

The original response records survived in a historical research snapshot after a
cleanup removed them from the working tree. This release contains those records;
it does not regenerate responses or infer them from aggregate numbers.

## Contents and verification

`published/study1-records.tar.gz` is a 2 MB archive containing:

- 38,700 responses in 630 evaluation files and their 630 summaries.
- Original and mirrored prompt sets, training pairs, and saved configurations.
- 98 training logs and adapter configurations; weights are linked separately below.
- The 120-response blinded judge sample, answer key, and recorded judge decisions.
- Eight Mistral capability-result files, 24 latent-measurement files, and four layer-gap profiles.

Run from the repository root with Python's standard library:

```bash
python scripts/verify_study1.py
python scripts/verify_study1.py --extract outputs/study1
```

The extraction destination must not exist. It receives `results/`, `data/`,
`configs/`, and `validation/`. Use these historical prompt sets when inspecting
the recovered responses. `example_id` identifies the prompt; `_mir_` filenames
use the mirrored ordering.

The verifier checks the archive and every file against
[`study1-manifest.json`](../published/study1-manifest.json), recomputes all 630
summary counts/rates from recorded labels, and joins the judge sample back to the
actual source responses. Its output is committed as
[`study1-verification.json`](../published/study1-verification.json).
[`study1-coverage.json`](../published/study1-coverage.json) inventories every
evaluation's model, filename, scenario, sample size and counts. Checksums establish
file identity; checking labels against summaries is not independent label validation.

All recovered response text and labels are unchanged. Eight capability-result files
omit an enclosing repository identifier and local installation prefixes; their
numeric results are unchanged. The manifest records original and exported hashes
and these transformations. Internal repository names and source commit IDs are not
included in the public provenance.

## Coverage is uneven

| Comparison | Recovered evidence |
|---|---|
| Mistral L16, last-token objective | Five seeds, 250 responses per seed for main, Treasure Hunt and Perspectives, in both room orders. Original main deception: 11.2%, 14.8%, 6.0%, 1.6%, 16.0%; mean 9.92%, sample SD 6.06 points. Mirrored main: 0% in all five seeds. |
| Mistral L19, full-sequence objective | Five seeds, 50 responses per main evaluation. Deception 4–20%, with 58–90% labeled other; original response text is included. |
| Gemma-2 L14 | Two seeds at 50 responses per scenario/order. This is not a five-seed, 250-item comparison. |
| Judge validation | 112/120 agreement (93.3%); eight disagreements are judge-other versus classifier-honest/deceptive, with no honest↔deceptive disagreement in this sample. The sample does not validate every evaluation condition. |
| Capability checks | Eight saved results: Mistral baseline, five L16 seeds, full-sequence L19 seed 0, and last-token L30 seed 0. Not every model variant was benchmarked. |

Across the archive, 594 evaluation files have 50 responses and 36 have 250.
The first post's former statement that every headline number used five seeds at
250 samples was too broad. Some sweeps have fewer seeds and incomplete mirrored
coverage. Consult the cell inventory rather than assuming a balanced experiment.

## Recovered Mistral adapters

All five Mistral L16 adapters are available in
[Arkonyx/soo-mistral-7b-l16](https://huggingface.co/Arkonyx/soo-mistral-7b-l16).
Seed 0 remains at the repository root; seeds 1–4 are in `seeds/seed1` through
`seeds/seed4`. [`study1-adapters.json`](../published/study1-adapters.json) pins the
Hub revision and every weight/config/training-log checksum.

Each training log and configuration matches its historical record byte-for-byte;
weight files match duplicate later frozen copies. The historical snapshot did not
contain weights, so it cannot independently establish historical weight checksums.
No retraining was performed. The original logs do not pin a base-model revision.

Download all five adapters at the verified revision:

```bash
hf download Arkonyx/soo-mistral-7b-l16 \
  --revision 03892943d80706f2f57a611428ac7b67a6ea6bac \
  --local-dir artifacts/adapters/mistral-l16-five-seeds
```

After downloading the pinned revision, pass the appropriate seed directory to the
[evaluation commands](EXPERIMENTS.md). Evaluate both room orders and use the
historical prompt files extracted above when comparing to first-study responses.

## Remaining limits

No matched weights were found for the other 93 recorded checkpoint runs in the
searched home/worktree/scratch locations or tracked Git objects. Their recovered
logs and configurations support retraining, which would be a new replication rather
than recovery of the original weights. This snapshot is not proof of completeness
for every run ever performed. Full activation tensors, complete original environments,
and full judge request metadata are not supplied. The saved representation summaries
and capability scores can be inspected, but do not by themselves rerun those measurements.
