# Release provenance and validation

Prepared October 21, 2026 from the research implementation used for the posts.
Original and released file hashes are recorded in `SOURCE_MANIFEST.json`.
Internal repository identifiers and source locations are omitted from the public
manifest; a complete mapping is retained privately by the release maintainer.

Packaging changes:

- Selected the SOO modules, configs, synthetic data, measurement/analysis scripts,
  and existing CPU tests required by the two posts.
- Renamed the import package to `soo_experiments` to allow installation alongside
  the companion `axis_rh` package. All scripts and commands use the new namespace.
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

Version 0.2.0 removes internal source identifiers from current release files,
credits contributors in the MIT copyright notice, and uses a distinct import namespace.
The existing test suite passes after the rename. Earlier Git commits are not rewritten.

The response verifier reproduces all counts and rates from 459,250 original responses
across 1,837 second-study evaluation files. The first study's complete response archive
remains unavailable. Both distributions were also installed together in a fresh
environment, and their package files do not overlap.
