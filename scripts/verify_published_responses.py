"""Recount every published SOO response using only the Python standard library."""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--published', type=Path, default=ROOT / 'published')
    parser.add_argument('--extract-run', help='Optional run ID to extract for the original response-analysis scripts')
    parser.add_argument('--out', type=Path, default=ROOT / 'outputs' / 'response-review')
    args = parser.parse_args()
    manifest_path = args.published / 'study2-responses-manifest.json'
    if not manifest_path.exists():
        parser.error('Response bundle not installed. See docs/RESULTS.md for availability; use --published to point to an extracted bundle.')
    manifest = json.loads(manifest_path.read_text())
    archive = args.published / manifest['archive']
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest['archive_sha256']:
        raise ValueError('Response archive checksum mismatch')
    expected = {(r['run'], r['file'].replace('_summary.json', '.jsonl')): r
                for r in json.loads((args.published / 'study2-summaries.json').read_text())}
    if args.extract_run and args.extract_run not in {run for run, _ in expected}:
        parser.error('Unknown run ID; see published/study2-runs.json')
    counts = defaultdict(Counter)
    seen = set()
    extracted = defaultdict(list)
    with gzip.open(archive, 'rt', encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            key = r['run'], r['file']
            if key not in expected:
                raise ValueError(f'Unexpected run/file: {key}')
            identity = (*key, r['example_id'])
            if identity in seen:
                raise ValueError(f'Duplicate response: {identity}')
            seen.add(identity)
            counts[key][r['label']] += 1
            if r['run'] == args.extract_run:
                if Path(r['file']).name != r['file']:
                    raise ValueError('Expected a filename without directory components')
                extracted[r['file']].append({k: r[k] for k in ('example_id', 'response', 'label')})
    if set(counts) != set(expected) or len(seen) != manifest['records']:
        raise ValueError('Incomplete response archive')
    for key, summary in expected.items():
        if dict(counts[key]) != {k: v for k, v in summary['counts'].items() if v} or sum(counts[key].values()) != summary['n']:
            raise ValueError(f'Counts differ from the published summary: {key}')
        for label, rate in summary.get('rates', {}).items():
            if abs(counts[key][label] / summary['n'] - rate) > 1e-12:
                raise ValueError(f'Rate differs from the published summary: {key}, {label}')
    # Write only after the entire archive has passed validation.
    if extracted:
        dest = args.out / args.extract_run / 'output' / 'eval'
        dest.mkdir(parents=True, exist_ok=True)
        for filename, rows in extracted.items():
            target = dest / filename
            content = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
            if target.exists() and target.read_text() != content:
                raise FileExistsError(f'Refusing to overwrite changed responses: {target}')
            target.write_text(content)
        print(f'Extracted {len(extracted)} files to {dest}')
    print(f'Verified {len(seen):,} responses across {len(counts):,} evaluation files.')


if __name__ == '__main__':
    main()
