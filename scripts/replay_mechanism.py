"""Replay archived CPU analyses in a temporary copy and compare their JSON results."""
import argparse
import json
from pathlib import Path
import runpy
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def comparable(value):
    if isinstance(value, dict):
        result = {k:comparable(v) for k,v in value.items() if k != 'note'}
        # Older complete verdicts omitted the now-explicit false flag.
        if 'reproduces_adapter' in result and isinstance(result.get('checks'), dict):
            if result['checks'] and all(isinstance(v, dict) for v in result['checks'].values()):
                result.setdefault('incomplete', False)
        return result
    if isinstance(value, list):
        return [comparable(v) for v in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study2', type=Path, help='Extracted study2 directory')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT/'experiments/soo/scripts'))
    runs = [r['run'] for r in json.loads((ROOT/'published/study2-runs.json').read_text())]
    count = 0
    with tempfile.TemporaryDirectory(prefix='soo-replay-') as tmp:
        for name in runs:
            source = args.study2/name
            archived = sorted((source/'output').rglob('analysis.json'))
            if not archived or name.startswith('subspace-'):
                continue
            run = Path(tmp)/name
            shutil.copytree(source, run, ignore=shutil.ignore_patterns('*.pt','*.safetensors'))
            launch = json.loads((run/'launch.json').read_text())
            for original in archived:
                result = run/original.relative_to(source)
                output = result.parent
                family = name.split('-')[0]
                script, extra = {
                    'adapters': ('analyze_adapter_round.py', []),
                    'constants': ('analyze_constant_round.py', []),
                    'layers': ('analyze_layer_round.py', [str(launch.get('layer'))]),
                    'bisect': ('analyze_bisect_round.py', [str(launch.get('layer')),str(run/'launch.json')]),
                    'bisect2': ('analyze_bisect_round.py', [str(launch.get('layer')),str(run/'launch.json')]),
                    'qwenloc': ('analyze_bisect_round.py', [str(launch.get('layer')),str(run/'launch.json')]),
                    'steer': ('analyze_steer_round.py', [str(run/'launch.json')]),
                    'dose': ('analyze_steer_round.py', [str(run/'launch.json')]),
                    'kimi': ('analyze_kimi_round.py', [str(run/'launch.json')]),
                    'kimisweep': ('analyze_kimi_sweep.py', [str(run/'launch.json')]),
                    'kimiloc': ('analyze_kimi_loc.py', [str(run/'launch.json')]),
                    'kimijoint': ('analyze_kimi_joint.py', [str(run/'launch.json')]),
                }[family]
                script_path = ROOT/'experiments/soo/scripts'/script
                sys.argv = [str(script_path),str(output),*extra]
                runpy.run_path(str(script_path), run_name='__main__')
                if comparable(json.loads(result.read_text())) != comparable(json.loads(original.read_text())):
                    raise ValueError(f'Replayed analysis differs: {original}')
                count += 1
                print(f'Matched {name}/{original.relative_to(source)}', flush=True)
    if not count:
        raise ValueError('No analyses found')
    print(f'Matched {count} archived analyses (methodology notes excluded; omitted false completeness flags normalized).')


if __name__ == '__main__':
    main()
