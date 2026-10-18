#!/usr/bin/env python3
"""Sort immediate image files into raw/ and jpg/ without overwriting files."""

import argparse
from dataclasses import dataclass
import logging
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys

RAW_EXTENSIONS = {'.cr2', '.cr3', '.arw', '.nef', '.nrw'}
JPG_EXTENSIONS = {'.jpg', '.jpeg'}
LOG_PATH = Path.home() / 'Library/Logs/image_split.log'
log = logging.getLogger('image_split')


@dataclass
class Result:
    raw: int = 0
    jpg: int = 0
    skipped: int = 0
    failed: int = 0


def unlock_file(path):
    """Clear only the user immutable flag on macOS, when necessary."""
    if sys.platform == 'darwin':
        flags = path.stat(follow_symlinks=False).st_flags
        if flags & stat.UF_IMMUTABLE:
            os.chflags(path, flags & ~stat.UF_IMMUTABLE, follow_symlinks=False)
            log.info('Unlocked %s', path)


def move_file(src, dst_dir):
    # Refuse symlink destinations, which could send images outside the folder.
    if dst_dir.is_symlink():
        raise ValueError(f'Destination is a symbolic link: {dst_dir}')
    dst_dir.mkdir(exist_ok=True)
    counter = 0
    while True:
        name = src.name if counter == 0 else f'{src.stem}_{counter}{src.suffix}'
        dst = dst_dir / name
        try:
            # Reserve the filename atomically, including against concurrent runs.
            fd = os.open(dst, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            counter += 1
            continue
        os.close(fd)
        break
    try:
        unlock_file(src)
        shutil.move(str(src), str(dst))
    except Exception:
        dst.unlink()
        raise
    log.info('Moved %s -> %s', src, dst)


def process_folder(folder):
    folder = Path(os.path.abspath(os.path.expanduser(folder)))
    if not folder.is_dir():
        raise ValueError(f'Not a directory: {folder}')
    result = Result()
    for entry in folder.iterdir():
        if entry.is_symlink() or not entry.is_file():
            continue
        ext = entry.suffix.lower()
        kind = 'raw' if ext in RAW_EXTENSIONS else 'jpg' if ext in JPG_EXTENSIONS else None
        if kind is None:
            result.skipped += 1
            continue
        try:
            move_file(entry, folder / kind)
            setattr(result, kind, getattr(result, kind) + 1)
        except Exception:
            result.failed += 1
            log.exception('Failed to move %s', entry)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--notify', action='store_true', help='Show a macOS completion notification')
    parser.add_argument('folders', nargs='+', help='Folders to sort (nonrecursive)')
    args = parser.parse_args(argv)
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(message)s')
    except OSError as exc:
        logging.basicConfig(level=logging.INFO)
        log.warning('Cannot open log file: %s', exc)
    failed = 0
    moved = 0
    for folder in args.folders:
        try:
            result = process_folder(folder)
            moved += result.raw + result.jpg
            failed += result.failed
            print(f'{folder}: RAW {result.raw}, JPG {result.jpg}, '
                  f'other files left in place {result.skipped}, failed {result.failed}')
        except Exception as exc:
            failed += 1
            log.exception('Cannot process %s', folder)
            print(f'{folder}: {exc}', file=sys.stderr)
    if args.notify and sys.platform == 'darwin':
        # Only generated counts enter AppleScript, never user-controlled paths.
        message = f'{moved} images sorted; {failed} failures. See image_split.log for details.'
        try:
            subprocess.run(['/usr/bin/osascript', '-e',
                            f'display notification "{message}" with title "ImageSplit"'],
                           check=False, timeout=15)
        except (OSError, subprocess.TimeoutExpired):
            log.warning('Could not display completion notification')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
