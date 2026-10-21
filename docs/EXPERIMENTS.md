# Experiment map and commands

Layer indices are zero-based. Run the commands below from `experiments/soo`, with
the repository installed into the active Python environment. The scripts keep the
original `selfconcept` import paths so existing adapters and results remain compatible.
Install the two research repositories in separate environments because both use that
namespace.

## First post: replication and evaluation confounds

| Component | Code / input |
|---|---|
| Matched self/other pairs and room scenarios | `src/selfconcept/soo/{datagen,scenarios,vocab}.py` |
| LoRA training; full-sequence vs final-token MSE | `src/selfconcept/soo/train.py` |
| Original, mirrored, transfer and Perspectives evaluations | `src/selfconcept/soo/evaluate.py`, `data/eval*` |
| Training recipes and ablations | `configs/*.yaml`; CLI `--layer`, `--epochs`, `--seeds` |
| Base activation-gap profile | `scripts/layer_gap.py MODEL OUTPUT.json` |
| Paired item comparisons | `scripts/paired_tests.py A.jsonl B.jsonl --field label --positive deceptive` |
| Reclassification of archived evaluations | `scripts/rescore.py --dry-run` (omit flag to rewrite results) |

The original-paper Mistral recipe is `mistral-7b.yaml` at layer 19 with full-sequence
loss. `mistral-7b-lasttok.yaml` changes the loss endpoint; explicitly select layer 16
for the robust cell. The Gemma-2 recipe is `gemma2-27b.yaml`: compare its original
layer 20 with the working layer 14. OLMo and Muse configs preserve their tested
starting recipes; neither should be described as having a uniformly successful cell.
The Mistral epoch, learning-rate and 4-bit configs encode the individual ablations.

Example layer sweep (training only; evaluate both orderings afterward):

```bash
for layer in 14 16 18 19 20; do
  python -m selfconcept.soo.train --config configs/mistral-7b-lasttok.yaml \
    --layer "$layer" --seeds 0 1 2 3 4
done
```

The first post's capability checks use the external `lm_eval` harness (optional
`capabilities` dependencies), with ARC, HellaSwag and MMLU. The second post did not
run capability benchmarks. Its Perspectives control is a task-specific theory-of-mind
check, not a general capability guarantee. The archived LLM-judge calls and raw model
outputs are not bundled in this release.

## Second post: selected adapters

| Model | Config | Training layer | Seed in localization study | Working subset |
|---|---|---:|---:|---|
| Mistral-7B-Instruct-v0.2 | `mistral-7b-lasttok.yaml` | 16 | 0 | `range:5-13`, `v_proj` |
| Gemma-4-12B | `gemma4-12b.yaml` | 24 | 0 | `range:19-23`, `v_proj` |
| Gemma-4-31B | `gemma4-31b.yaml` | 32 | 0 | `range:20-31`, `v_proj` |
| Qwen3.8-27B | `qwen38-27b.yaml` | 32 | 0 | `range:24-31`, all trained modules |
| Kimi-Dev-72B | `kimi-dev-72b.yaml` | 56 | 0 | `below:56`, both query and value |

The two Gemma configs retain earlier default layers, and Kimi defaults to 40.
Always supply the training-layer override from the table. Qwen's fused
`in_proj_qkv` includes query/key/value channels in its DeltaNet blocks; pretending
it has ordinary `q_proj` and `v_proj` at every layer changes the experiment.
`lora_subset.py` and `steering.py` support the fused-channel selections used here.

For Gemma and Qwen, the experiment used thinking disabled. Set this explicitly:

```bash
export SOO_CHAT_KWARGS='{"enable_thinking": false}'
python -m selfconcept.soo.train --config configs/gemma4-12b.yaml --layer 24 --seeds 0
```

For Kimi use its own config without imposing another model's chat-template settings;
the evaluator uses the text after its `<think>` block and records truncation. Use
`--max-new-tokens 1024 --suffix room_only --device-map auto`. The training config
shards the 72B model across available GPUs. The other mechanism-study models use
`room_only`, except Mistral which uses `i_would`.

### Adapter localization

After training Gemma-4-12B at layer 24:

```bash
python -m selfconcept.soo.evaluate --model google/gemma-4-12B-it \
  --adapter results/checkpoints/gemma4-12b-L24/seed0 \
  --adapter-layers range:19-23 --adapter-modules v_proj \
  --scenarios main treasure_hunt perspectives --data data/eval \
  --suffix room_only --n 250 --tag value-band-original
```

Repeat with `data/eval_mirrored` and a different tag. Compare `only:24`, `above:24`,
`below:24`, `q_proj`, and `v_proj` against the full adapter and base model.
Ranges are inclusive. Available layer expressions include `all`, `only:L`,
`except:L`, `below:L`, `above:L`, `range:A-B`, and `layers:3,5`.

### Constant replacement at the training layer

```bash
python scripts/make_constants.py --model google/gemma-4-12B-it --layer 24 \
  --pairs data/train_soo_pairs.jsonl \
  --adapter adapter_seed0=results/checkpoints/gemma4-12b-L24/seed0 \
  --out results/constants/gemma4-12b.pt
python -m selfconcept.soo.evaluate --model google/gemma-4-12B-it \
  --steer-layer 24 --steer-mode replace \
  --steer-constants results/constants/gemma4-12b.pt --steer-constant adapter_seed0 \
  --scenarios main perspectives --suffix room_only --n 250 --tag constant-original
```

This runs without the adapter. Compare with `base_mean`, `zero`, and matched-norm
random constants, and repeat both orderings. Mistral requires the additional intent
check in `scripts/intent_language_check.py` because first-room scoring can mislabel
confused answers as honest.

### Replace a value band with fixed offsets

```bash
python scripts/extract_band_deltas.py --model google/gemma-4-12B-it \
  --adapter results/checkpoints/gemma4-12b-L24/seed0 \
  --layers range:19-23 --modules v_proj --pairs data/train_soo_pairs.jsonl \
  --out results/band-deltas/gemma4-12b.pt
python -m selfconcept.soo.evaluate --model google/gemma-4-12B-it \
  --band-deltas results/band-deltas/gemma4-12b.pt --band-module v_proj \
  --band-token-mode all --band-alpha 1 --steer-positions prompt \
  --scenarios main treasure_hunt perspectives --suffix room_only --n 250 \
  --tag fixed-offset-original
```

Repeat with `--band-random-seed 0`, with response-only positions, and in the mirrored
ordering. These are reusable intervention commands, not a claim that every model's
successful dose is one. Original per-run conditions are recorded in
`published/study2-runs.json`; compare the exact dose and positions before reproducing
a particular table cell. Kimi's joint offsets need both projections and the separate
content-token position condition.

### Self/other and name-control gaps

From the repository root, `python experiments/soo/scripts/prepare_subspace_pilot.py`
verifies/regenerates the committed probe file (refusing to overwrite a different one).
Then, from `experiments/soo`:

```bash
python -m selfconcept.soo.measure_overlap --model google/gemma-4-12B-it \
  --probes data/subspace_pilot_pairs.jsonl --split development --layer 24 \
  --adapter results/checkpoints/gemma4-12b-L24/seed0 \
  --device cuda --dtype bfloat16 --out results/overlap/gemma4-12b
```

The development set contains 32 self/other pairs and 32 name-control pairs.
Gap, spread and output norm are distinct measurements. `--endpoint-offset` changes
the token measured. `--subspace-ranks` enables fitted subspace removal controls.
The `analyze_*_round.py` scripts retain the original frozen-run analysis interfaces;
they expect the corresponding run manifest and raw outputs, not only the public
aggregate summary. Those raw outputs are not bundled.
