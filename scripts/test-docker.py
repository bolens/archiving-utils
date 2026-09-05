#!/usr/bin/env python3
"""Exercise the built CLI image on disposable bind mounts, without networking."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

SUITE = 'archiving-utils'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', default='docker')
    parser.add_argument('--image', default=SUITE + ':local')
    args = parser.parse_args()
    uid = os.getuid() or 10001
    gid = os.getgid() if os.getuid() else 10001
    with tempfile.TemporaryDirectory(prefix=SUITE + '-docker-') as tmp:
        root = Path(tmp)
        root.chmod(0o755)
        inputs, outputs = root / 'input', root / 'output'
        inputs.mkdir()
        outputs.mkdir()
        if os.getuid() == 0:
            os.chown(outputs, uid, gid)
        options = ['--rm', '--network=none', '--read-only', '--cap-drop=ALL',
                   '--security-opt=no-new-privileges', '--tmpfs', '/tmp:rw,nosuid,nodev,mode=1777',
                   '--user', f'{uid}:{gid}', '--workdir', '/output',
                   '--mount', f'type=bind,src={inputs},dst=/input,readonly',
                   '--mount', f'type=bind,src={outputs},dst=/output']
        if Path(args.engine).name == 'podman':
            options += ['--userns=keep-id']

        def run(*command, entry=None, code=0, default_user=False):
            opts = options.copy()
            if default_user:
                i = opts.index('--user')
                del opts[i:i + 2]
            if entry:
                opts += ['--entrypoint', entry]
            result = subprocess.run([args.engine, 'run', *opts, args.image, *map(str, command)],
                                    capture_output=True, text=True, timeout=180)
            if result.returncode != code:
                raise AssertionError(f'{command!r}: expected {code}, got {result.returncode}\n'
                                     f'{result.stdout}\n{result.stderr}')
            return result.stdout

        def unchanged(path, original):
            if path.read_bytes() != original:
                raise AssertionError(f'Source changed: {path.name!r}')

        def owned(path):
            if path.stat().st_uid != uid or path.stat().st_gid != gid:
                raise AssertionError(f'Output ownership differs from {uid}:{gid}: {path}')

        if run('-u', entry='id', default_user=True).strip() != '10001':
            raise AssertionError('Image must default to UID 10001')
        run('--help')
        run('not-a-tool', code=2)
        run('--version')
        pages = inputs / 'pages'
        pages.mkdir()
        (pages / 'empty').mkdir()
        name = '-雪 [*]\n.jpg'
        (pages / name).write_bytes(b'opaque page payload')
        (pages / 'ComicInfo.xml').write_bytes(b'<ComicInfo/>')
        for fmt in ('cbz', 'cb7', 'cbt', 'cbt-gz', 'cbt-bz2', 'cbt-xz', 'cbt-zst'):
            target = '/output/book.' + fmt.replace('-', '.')
            run('folder-to-' + fmt, '-o', target, '/input/pages')
            if (outputs / Path(target).name).exists():
                raise AssertionError('Planning wrote an archive')
            run('folder-to-' + fmt, '--apply', '-o', target, '/input/pages')
            before = (outputs / Path(target).name).read_bytes()
            run('folder-to-' + fmt, '--apply', '-o', target, '/input/pages', code=1)
            unchanged(outputs / Path(target).name, before)
            run('comic-verify', target)
            run('comic-extract', '--apply', '-o', '/output/unpacked-' + fmt, target)
            extracted = outputs / ('unpacked-' + fmt)
            if (extracted / name).read_bytes() != b'opaque page payload':
                raise AssertionError('Page name or bytes changed')
            if not (extracted / 'empty').is_dir():
                raise AssertionError('Empty directory lost')
            if (extracted / 'ComicInfo.xml').read_bytes() != b'<ComicInfo/>':
                raise AssertionError('Sidecar changed')
            owned(extracted / name)
        unchanged(pages / name, b'opaque page payload')
        (inputs / 'bad.cbz').write_bytes(b'not an archive')
        run('comic-extract', '--apply', '-o', '/output/failed', '/input/bad.cbz', code=1)
        if (outputs / 'failed').exists():
            raise AssertionError('Failed operation published output')
        print(SUITE + ': Docker acceptance passed (no skips)')


if __name__ == '__main__':
    main()
