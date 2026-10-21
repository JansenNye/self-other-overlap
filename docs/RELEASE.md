# Release provenance and validation

Prepared October 21, 2026 from the SOO research implementation. Original
file hashes are retained in `SOURCE_MANIFEST.json`. This implementation
contains the Kimi dose/position and Qwen fused-projection support used by the second
post. The newer main research branch did not contain all of those changes.

Packaging changes:

- Selected the SOO modules, configs, synthetic data, measurement/analysis scripts,
  and existing CPU tests required by the two posts.
- Kept `selfconcept` module names; use a separate environment from the companion repo.
- Removed import-time cluster detection, forced offline mode and `byutils` side effects.
- Made scratch storage configurable with `SELFCONCEPT_SCRATCH` and supplied a generic
  Slurm wrapper instead of hardcoding a partition, account, cache, or GPU assignment.
- Forwarded revision/cache options to model configuration loading, and ensured the
  training model respects a configured revision in every loading mode.
- Added dependency metadata, MIT licensing, experiment commands, source hashes,
  aggregate result exports and a data-driven plotting script.

Validation uses Python 3.13.7 and the versions in `requirements-tested.txt` on the
cluster. The existing 69 tests use tiny random models and temporary inputs. They cover
LoRA subsets, fused QKV selections, fixed-offset extraction/interventions, positional
masks, post-thinking classification, constant replacement, and overlap/subspace math.
The plot is generated from the exported counts. Full model training and evaluation
were not repeated during packaging; archived result exports are not fresh replications.

The source research worktree is kept separate and unchanged by this release.

Both wheel and source distributions build successfully with `uv build`.
