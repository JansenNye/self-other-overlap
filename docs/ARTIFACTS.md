# Data and trained adapters

## Raw evaluation responses

The second study's 459,250 saved responses are committed in
[`published/study2-responses.jsonl.gz`](../published/study2-responses.jsonl.gz), with
checksums and per-file provenance. See [RESULTS.md](RESULTS.md) for the standard-library
verifier, response extraction, and intent-language analysis commands. The separate [first-study archive](STUDY1.md) adds 38,700 recovered responses,
training logs, judge decisions, and capability results. Its coverage is explicitly
inventoried rather than assumed complete.

## Five trained adapters

Five seed-0 adapters are publicly available with original weights, PEFT configs, training
logs, SHA-256 manifests, model cards, and base-model license notices. Immutable Hub
revisions and weight checksums are recorded in [`published/adapters.json`](../published/adapters.json).

| Adapter | Training layer | Base model | Weight size |
|---|---:|---|---:|
| [Mistral](https://huggingface.co/Arkonyx/soo-mistral-7b-l16) | 16 | `mistralai/Mistral-7B-Instruct-v0.2` | 13.6 MB |
| [Gemma 12B](https://huggingface.co/Arkonyx/soo-gemma4-12b-l24) | 24 | `google/gemma-4-12B-it` | 10.4 MB |
| [Gemma 31B](https://huggingface.co/Arkonyx/soo-gemma4-31b-l32) | 32 | `google/gemma-4-31B-it` | 21.9 MB |
| [Qwen](https://huggingface.co/Arkonyx/soo-qwen38-27b-l32) | 32 | `Qwen/Qwen3.8-27B` | 17.9 MB |
| [Kimi](https://huggingface.co/Arkonyx/soo-kimi-dev-72b-l56) | 56 | `moonshotai/Kimi-Dev-72B` | 32.8 MB |

New adapter contributions use MIT; the accompanying base-model terms and notices are
preserved. The bundles contain no base weights. These are the complete adapters;
select module/layer subsets using the [experiment commands](EXPERIMENTS.md).
No model training was rerun to create these bundles.

## Download and evaluate an adapter

From the repository root after installation (GPU resources are needed for evaluation):

```bash
hf download Arkonyx/soo-gemma4-12b-l24 --revision a24451b26958ff756118ccc97f40a8d4883d322a \
  --local-dir artifacts/adapters/gemma4-12b-L24
export SOO_CHAT_KWARGS='{"enable_thinking": false}'
python -m soo_experiments.soo.evaluate --model google/gemma-4-12B-it \
  --adapter artifacts/adapters/gemma4-12b-L24 \
  --data experiments/soo/data/eval --scenarios main treasure_hunt perspectives \
  --suffix room_only --n 250 --tag public-adapter-original
```

Repeat with `experiments/soo/data/eval_mirrored` and a different tag. Use the model,
revision, and checksum entries in the artifact manifest for the other adapters.
The base-model identifier, loss, layer, and generation settings must match the
[experiment map](EXPERIMENTS.md); a Hub adapter revision pins the adapter, not its base model.

## First-study Mistral seeds

The Mistral Hub repository now also includes seeds 1–4 in `seeds/seed1` through
`seeds/seed4`. Seed 0 remains at the root, so the older pinned downloads above
remain valid. See [STUDY1.md](STUDY1.md) and
[`published/study1-adapters.json`](../published/study1-adapters.json) for the new
pinned revision, checksums, provenance limits, and first-study coverage.
