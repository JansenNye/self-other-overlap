"""Verify recovered first-study records without ML dependencies or model downloads."""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import statistics
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def verify(archive, manifest):
    raw = archive.read_bytes()
    if hashlib.sha256(raw).hexdigest() != manifest['sha256']:
        raise ValueError('Archive checksum mismatch')
    expected = {f['path']: f for f in manifest['files']}
    if len(expected) != len(manifest['files']):
        raise ValueError('Duplicate manifest paths')
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or member.name in files:
                raise ValueError(f'Unsafe or duplicate member: {member.name}')
            data = tar.extractfile(member).read()
            if member.name not in expected or hashlib.sha256(data).hexdigest() != expected[member.name]['sha256']:
                raise ValueError(f'File checksum mismatch: {member.name}')
            if len(data) != expected[member.name]['bytes']:
                raise ValueError(f'File size mismatch: {member.name}')
            files[member.name] = data
    if set(files) != set(expected):
        raise ValueError('Archive inventory mismatch')
    responses, cells = {}, []
    for name, data in sorted(files.items()):
        if not name.startswith('results/eval/') or not name.endswith('.jsonl'):
            continue
        records = [json.loads(line) for line in data.splitlines()]
        by_id = {r['example_id']: r for r in records}
        if len(by_id) != len(records) or not records:
            raise ValueError(f'Empty evaluation or duplicate example IDs: {name}')
        summary = json.loads(files[name[:-6] + '_summary.json'])
        counts = Counter(r['label'] for r in records)
        if not set(counts) <= {'honest', 'deceptive', 'refusal', 'other'}:
            raise ValueError(f'Unknown label: {name}')
        if len(records) != summary['n']:
            raise ValueError(f'Sample size mismatch: {name}')
        for label in set(counts) | set(summary['counts']):
            if counts[label] != summary['counts'].get(label, 0):
                raise ValueError(f'Count mismatch: {name}: {label}')
            if abs(counts[label] / len(records) - summary['rates'][label]) > 0.000051:
                raise ValueError(f'Rate mismatch: {name}: {label}')
        responses[Path(name).name] = by_id
        cells.append({'file': Path(name).name, 'model': summary['model'], 'scenario': summary['scenario'],
                      'n': len(records), 'counts': dict(counts)})
    keys = {r['sample_id']: r for r in map(json.loads, files['validation/key.jsonl'].splitlines())}
    samples = {r['sample_id']: r for r in map(json.loads, files['validation/sample.jsonl'].splitlines())}
    judges = {r['sample_id']: r for r in map(json.loads, files['validation/judge.jsonl'].splitlines())}
    if set(keys) != set(samples) or set(keys) != set(judges):
        raise ValueError('Judge sample coverage differs')
    confusion = Counter()
    for sample_id, key in keys.items():
        source = responses[key['source_file']][key['example_id']]
        if source['response'] != samples[sample_id]['response'] or source['label'] != key['classifier_label']:
            raise ValueError(f'Judge sample differs from source response: {sample_id}')
        judge = judges[sample_id]
        label = 'other'
        if judge['category'] == 'refusal':
            label = 'refusal'
        elif judge['category'] == 'room':
            if judge['answer_room'] == key['honest']:
                label = 'honest'
            elif judge['answer_room'] == key['deceptive']:
                label = 'deceptive'
        confusion[f'{label}/{key["classifier_label"]}'] += 1
    def rates(pattern):
        selected = [c for c in cells if PurePosixPath(c['file']).match(pattern)]
        return [100 * c['counts'].get('deceptive', 0) / c['n'] for c in selected]
    main = rates('soo_mistral7b_lasttok_L16_seed[0-4]_n250_main_i_would.jsonl')
    mirrored = rates('soo_mistral7b_lasttok_L16_seed[0-4]_mir_n250_main_i_would.jsonl')
    if len(main) != 5 or len(mirrored) != 5:
        raise ValueError('Incomplete five-seed Mistral comparison')
    report = {'files': len(files), 'evaluation_files': len(cells), 'responses': sum(c['n'] for c in cells),
              'evaluation_file_counts_by_n': dict(Counter(c['n'] for c in cells)),
              'evaluation_file_counts_by_model': dict(Counter(c['model'] for c in cells)),
              'mistral_l16_original_deception_percent': main,
              'mistral_l16_mean_percent': statistics.mean(main),
              'mistral_l16_sample_sd_percent': statistics.stdev(main),
              'mistral_l16_mirrored_deception_percent': mirrored,
              'judge_samples': len(keys), 'judge_agreement': sum(n for pair,n in confusion.items() if len(set(pair.split('/'))) == 1),
              'judge_confusion_judge_classifier': dict(confusion),
              'training_logs': sum(n.endswith('/train_log.json') for n in files),
              'capability_files': sum(n.startswith('results/capabilities/') for n in files),
              'latent_measurement_files': sum(n.startswith('results/latent/') for n in files),
              'interpretation': 'Verifies checksums, recorded labels against summaries, and saved judge agreement; does not independently adjudicate labels or regenerate model outputs.'}
    return report, cells, files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT/'published/study1-records.tar.gz')
    parser.add_argument('--manifest', type=Path, default=ROOT/'published/study1-manifest.json')
    parser.add_argument('--extract', type=Path, help='New directory for the verified historical inputs and records')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--coverage', type=Path, help='Write every recovered evaluation cell, sample size and count')
    args = parser.parse_args()
    report, cells, files = verify(args.archive, json.loads(args.manifest.read_text()))
    if args.extract:
        args.extract.mkdir(parents=True, exist_ok=False)
        for name, data in files.items():
            target = args.extract / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    text = json.dumps(report, indent=2) + '\n'
    if args.report:
        args.report.write_text(text)
    if args.coverage:
        args.coverage.write_text(json.dumps(cells, indent=2) + '\n')
    print(text)


if __name__ == '__main__':
    main()
