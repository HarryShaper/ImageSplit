#!/usr/bin/env python3
"""Build a prototype macOS package using a supplied standalone Python runtime."""

import argparse
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
INSTALL = '/Library/Application Support/ImageSplit'
COMMAND = f'exec "{INSTALL}/runtime/bin/python3" "{INSTALL}/image_split.py" --notify -- "$@"'


def workflow():
    return {
        'AMApplicationBuild': '523',
        'AMApplicationVersion': '2.10',
        'AMDocumentVersion': '2',
        'actions': [{
            'action': {
                'AMAccepts': {'Container': 'List', 'Optional': True, 'Types': ['com.apple.cocoa.path']},
                'AMActionVersion': '2.0.3',
                'AMApplication': ['Automator'],
                'AMParameterProperties': {},
                'AMProvides': {'Container': 'List', 'Types': ['com.apple.cocoa.string']},
                'ActionBundlePath': '/System/Library/Automator/Run Shell Script.action',
                'ActionName': 'Run Shell Script',
                'ActionParameters': {'COMMAND_STRING': COMMAND, 'CheckedForUserDefaultShell': True,
                                     'inputMethod': 1, 'shell': '/bin/bash', 'source': ''},
                'BundleIdentifier': 'com.apple.RunShellScript',
                'CFBundleVersion': '2.0.3',
                'Class Name': 'RunShellScriptAction',
                'InputUUID': '0E1EED1B-232C-4772-A77C-D33288B1B6C4',
                'OutputUUID': '59CB13D1-4ABC-43D4-82B0-CBC5869FE871',
                'UUID': '67B777A1-51AF-40F2-BC1C-7CF1CA3E65FA',
                'isViewVisible': True,
            },
            'isViewVisible': True,
        }],
        'connectors': [],
        'workflowMetaData': {'applicationBundleID': 'com.apple.finder', 'applicationBundleIDsByPath': {'/System/Library/CoreServices/Finder.app': 'com.apple.finder'}, 'applicationPath': '/System/Library/CoreServices/Finder.app', 'applicationPaths': ['/System/Library/CoreServices/Finder.app'], 'inputTypeIdentifier': 'com.apple.Automator.fileSystemObject.folder', 'outputTypeIdentifier': 'com.apple.Automator.nothing', 'presentationMode': 15, 'processesInput': False, 'serviceApplicationBundleID': 'com.apple.finder', 'serviceApplicationPath': '/System/Library/CoreServices/Finder.app', 'serviceInputTypeIdentifier': 'com.apple.Automator.fileSystemObject.folder', 'serviceOutputTypeIdentifier': 'com.apple.Automator.nothing', 'serviceProcessesInput': False, 'systemImageName': 'NSActionTemplate', 'useAutomaticInputType': False, 'workflowTypeIdentifier': 'com.apple.Automator.servicesMenu'},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, required=True,
                        help='Relocatable macOS runtime directory containing bin/python3')
    parser.add_argument('--version', default='0.1.0')
    parser.add_argument('--output', type=Path, default=ROOT / 'dist/ImageSplit.pkg')
    parser.add_argument('--sign', help='Developer ID Installer identity for pkgbuild')
    args = parser.parse_args()
    if sys.platform != 'darwin':
        parser.error('The installer must be built on macOS with pkgbuild available.')
    runtime = args.runtime.resolve()
    python = runtime / 'bin/python3'
    if not python.is_file():
        parser.error('Runtime must contain bin/python3. Do not use a virtual environment.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='imagesplit-package-') as temp:
        stage = Path(temp) / 'root'
        app = stage / INSTALL.lstrip('/')
        app.mkdir(parents=True)
        # Preserve internal runtime symlinks; reject links relying on the builder's files.
        for entry in runtime.rglob('*'):
            if entry.is_symlink() and not entry.resolve().is_relative_to(runtime):
                parser.error(f'Runtime symlink escapes its directory: {entry}')
        shutil.copytree(runtime, app / 'runtime', symlinks=True)
        shutil.copy2(ROOT / 'image_split.py', app / 'image_split.py')
        # Test from the relocated runtime rather than the original path.
        subprocess.run([str(app / 'runtime/bin/python3'), '-I', '-c',
                        'import argparse, dataclasses, logging, pathlib, shutil, subprocess'], check=True)
        smoke = Path(temp) / 'smoke folder'
        smoke.mkdir()
        (smoke / 'sample.NEF').write_bytes(b'raw-test')
        (smoke / 'sample.JPG').write_bytes(b'jpeg-test')
        subprocess.run([str(app / 'runtime/bin/python3'), str(app / 'image_split.py'), str(smoke)], check=True)
        assert (smoke / 'raw/sample.NEF').read_bytes() == b'raw-test'
        assert (smoke / 'jpg/sample.JPG').read_bytes() == b'jpeg-test'
        contents = stage / 'Library/Services/Split RAW-JPEG.workflow/Contents'
        contents.mkdir(parents=True)
        (contents / 'document.wflow').write_bytes(plistlib.dumps(workflow()))
        info = {'CFBundleIdentifier': 'io.github.harryshaper.imagesplit.quickaction',
                'CFBundleName': 'Split RAW-JPEG', 'CFBundleVersion': args.version,
                'NSServices': [{'NSMenuItem': {'default': 'Split RAW-JPEG'},
                                'NSMessage': 'runWorkflowAsService',
                                'NSIconName': 'NSActionTemplate',
                                'NSBackgroundColorName': 'background',
                                'NSSendFileTypes': ['public.folder'],
                                'NSRequiredContext': {'NSApplicationIdentifier': 'com.apple.finder'}}]}
        (contents / 'Info.plist').write_bytes(plistlib.dumps(info))
        command = ['/usr/bin/pkgbuild', '--root', str(stage), '--install-location', '/',
                   '--identifier', 'io.github.harryshaper.imagesplit', '--version', args.version,
                   '--ownership', 'recommended']
        if args.sign:
            command += ['--sign', args.sign]
        subprocess.run(command + [str(args.output.resolve())], check=True)
    print(f'Built {args.output}. Validate on a clean Mac before distribution.')


if __name__ == '__main__':
    main()
