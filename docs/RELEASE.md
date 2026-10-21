# Release scope and checks

Includes SOO training/evaluation code, synthetic prompts, adapter interventions,
archived run plans, 459,250 second-study responses, and links to five trained adapters.
The first study's full multiseed response archive and representation tensors are not
included. See [EXPERIMENTS.md](EXPERIMENTS.md) for commands and table mappings,
[ANALYSIS.md](ANALYSIS.md) for decision rules, and [RESULTS.md](RESULTS.md) for data scope.

Validation uses Python 3.13 and `requirements-tested.txt`: CPU tests with tiny models,
response-count verification against all 1,837 summaries, and before/after replay of
32 archived round readouts (identical results after omitting the changed methodology note). Wheel and source distributions build. No new full-model
training or generation is claimed. The package is `soo_experiments`, so it can coexist
with `axis_rh`. Original/released file hashes are in `SOURCE_MANIFEST.json`.
