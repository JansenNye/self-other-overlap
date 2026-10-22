"""Verify recovered mechanism-study files and optionally extract them."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def checksum(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--records', type=Path, default=ROOT/'published/mechanism-records.tar.gz')
    parser.add_argument('--tensors', type=Path, help='Optional downloaded mechanism-tensors.tar.gz')
    parser.add_argument('--extract', type=Path, help='New destination directory')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'published/mechanism-manifest.json').read_text())
    paths = [args.records] + ([args.tensors] if args.tensors else [])
    identities = {a['file']:a for a in manifest['archives']}
    for path in paths:
        identity = identities[path.name]
        if path.stat().st_size != identity['bytes'] or checksum(path) != identity['sha256']:
            raise ValueError(f'Archive checksum/size mismatch: {path}')
    if args.extract:
        args.extract.mkdir(parents=True, exist_ok=False)
    total = 0
    for path in paths:
        tensors = path.name == 'mechanism-tensors.tar.gz'
        expected = {'study2/'+f['path']:f for f in manifest['files']
                    if (Path(f['path']).suffix in {'.pt','.safetensors'}) == tensors}
        seen = set()
        with tarfile.open(path, 'r|gz') as tar:
            for member in tar:
                name = PurePosixPath(member.name)
                if not member.isfile() or name.is_absolute() or '..' in name.parts or member.name in seen:
                    raise ValueError(f'Unsafe or duplicate member: {member.name}')
                data = tar.extractfile(member).read()
                f = expected.get(member.name)
                if f is None or len(data) != f['bytes'] or hashlib.sha256(data).hexdigest() != f['sha256']:
                    raise ValueError(f'File integrity mismatch: {member.name}')
                seen.add(member.name)
                if args.extract:
                    target = args.extract/member.name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
        if seen != expected.keys():
            raise ValueError(f'Archive inventory mismatch: {path}')
        total += len(seen)
    print(f'Verified {total} files from {len(manifest["runs"])} indexed runs.')
    print('Checksum verification does not rerun models or independently validate measurements.')


if __name__ == '__main__':
    main()
