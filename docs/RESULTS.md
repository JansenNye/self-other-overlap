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

## Check the individual responses

`published/study2-responses.jsonl.gz` contains **459,250 saved model responses**
from all 1,837 evaluation files represented by the summaries (about 17 MB compressed).
Each row preserves `example_id`, `response`, and the original `label`, and adds `run`
and `file` to identify the evaluation cell. The raw response text is unchanged.
`study2-responses-manifest.json` records each source file's hash and the archive hash.

Recompute every count and rate without installing ML dependencies:

```bash
python scripts/verify_published_responses.py
```

To inspect Mistral's constant-replacement outputs and rerun the existing intent-language
heuristic, extract the selected run and point the original analysis script at it:

```bash
python scripts/verify_published_responses.py \
  --extract-run constants-mistral-7b-L16-20260922T175427Z
python experiments/soo/scripts/intent_language_check.py \
  outputs/response-review/constants-mistral-7b-L16-20260922T175427Z
```

Use the committed original/mirrored scenario files and `example_id` to inspect the
underlying task. An original label is a recorded classifier decision, not a new human
annotation: read the response text to assess confusion, refusal, or deceptive intent.
The intent regex is exploratory and is not an independent ground-truth label.

## Remaining gaps

The response archive covers the second study, including its controls and exploratory
runs. It does not contain the first study's complete multi-seed archive, so it cannot
independently substantiate all first-post claims about damaged outputs. Those original
runs must be recovered or repeated. Trained adapters and representation tensors remain
separate inputs; response records alone do not reproduce representation-gap measurements.
The five selected adapters are linked in [ARTIFACTS.md](ARTIFACTS.md).
