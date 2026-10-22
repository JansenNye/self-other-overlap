# Recovered mechanism-study inputs

The response archive is now supplemented by saved inputs and outputs from all 30
runs indexed in `published/study2-runs.json`. The record archive contains launch
metadata, prompt/probe inputs, per-pair measurements, overlap summaries, training
logs/configurations, behavioral responses and archived analysis JSON. A separate
tensor archive contains saved activations, steering/intervention tensors and adapter
weights from those runs: 4,549 files in total, including 68 activation captures and
64 adapter weight files representing 29 distinct weight hashes. Repeated copies are
retained to preserve run layout. These are recovered artifacts; no training or model
evaluation was rerun for this release.

## CPU analysis

From the repository root:

```bash
python scripts/verify_mechanism.py --extract outputs/mechanism
python scripts/replay_mechanism.py outputs/mechanism/study2
```

The first command uses only Python's standard library and requires a new extraction
directory. The second requires the installed package and its declared dependencies;
use `requirements-tested.txt` for the recorded dependency versions. It runs the
archived analysis interfaces in a temporary copy, leaving the verified
extraction unchanged. The release check matched all 30 saved round-analysis outputs. It compares the
regenerated JSON to the archived JSON, omitting
methodology `note` fields that were clarified in the public code. Older complete
verdicts that omitted the now-explicit `incomplete: false` flag are normalized to
that value when all recorded checks are complete. No rates, intervals, decision
labels or positive incompleteness flags are ignored. The replay does not rerun
models or independently validate the measurements. Per-pair data are sufficient for
these CPU analyses; the large tensor download is optional.

The inventory and checksums are in
[`mechanism-manifest.json`](../published/mechanism-manifest.json). It covers every
exported file and distinguishes original and exported bytes. The raw behavioral
archive remains documented in [RESULTS.md](RESULTS.md).

## Saved tensors and adapters

Download instructions and a pinned Hub revision are recorded in
[`mechanism-artifact.json`](../published/mechanism-artifact.json). Pass the downloaded
`mechanism-tensors.tar.gz` to the verifier along with the bundled records. Download
the optional 3.6 GB tensor archive at the verified revision:

```bash
hf download Arkonyx/self-other-overlap-mechanism --repo-type dataset \
  --revision f7a59a014d282da2eda9db776ea075f87e5c697c \
  mechanism-tensors.tar.gz --local-dir outputs/mechanism-download
```

Then verify and extract:

```bash
python scripts/verify_mechanism.py \
  --tensors outputs/mechanism-download/mechanism-tensors.tar.gz \
  --extract outputs/mechanism-with-tensors
```

Both archives extract under `study2/`, preserving each run's data/output/adapter
layout. Saved `.pt` files should be loaded with `torch.load(..., weights_only=True)`.
Base-model weights are not included; their original access and license terms still
apply. The five selected adapters also retain their smaller standalone Hub releases
in [ARTIFACTS.md](ARTIFACTS.md).

## Provenance and limits

The exporter removed enclosing source-commit identities, copied-source hashes,
commands containing private installation paths, and working-tree status. It normalized
remaining local paths. Model revisions, run conditions, input identity hashes and
scientific numeric values are retained. Tensor values, shapes and dtypes were checked
against the original files; metadata normalization does not change them. Unchanged
files retain their original bytes and hashes. Source hashes document the historical
inputs even when a released metadata file has a different checksum.

This is a data release, not a complete copy of every frozen directory: duplicated
source trees, scheduler logs, tokenizer copies and base-model weights are omitted.
Use the public analysis code and consult [EXPERIMENTS.md](EXPERIMENTS.md) for the
mapping from run families to post tables. Historical launch metadata is descriptive;
it is not a portable job submission script. Some indexed runs were incomplete or
exploratory, so inclusion does not imply every planned condition completed. The
subspace pilot includes its saved fit/condition artifacts but is not part of the
round-analysis replay comparison. The first study's remaining missing weights and
other limits are documented separately in [STUDY1.md](STUDY1.md).
