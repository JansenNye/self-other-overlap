# Archived results

`published/study2-summaries.json` contains 1,837 aggregate evaluation records from
30 frozen mechanism-study run directories. Each record identifies its original run
and filename, source SHA-256, model, scenario, sample size, counts and rates.
These include exploratory runs and controls, not only the successful cells.

`published/study2-runs.json` preserves the available model/revision, training layer,
conditions, orientation and scenario metadata from those run manifests. Some manifests
use different field names, so an omitted field means it was not exported; it is not
evidence that a setting had its default value. Source manifest hashes support comparison
with the original archives.

The plotting script selects the Gemma-4-12B bisection run
`bisect-gemma4-12b-L24-20260924T220341Z` and calculates rates from integer counts for
both room orderings. No rates are typed into the plotting code.

These aggregates do not include raw responses, trained adapters, activation tensors,
or the first study's complete multi-seed result archive. The first study's training
and evaluation code, ablation configs, and synthetic prompts are included. Regenerating
its numerical results requires running those experiments. The second study's counts
alone cannot reproduce intent-language checks, representation gaps, or bootstrap
analyses that require individual responses/activations.
