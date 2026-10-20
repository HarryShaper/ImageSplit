# ImageSplit

Sort images into `raw/` and `jpg/` inside the selected folder, without renaming
the folder. Supports Canon `.cr2`/`.cr3`, Sony `.arw`, Nikon `.nef`/`.nrw`, and
`.jpg`/`.jpeg`, regardless of extension case. Requires Python 3.10 or newer.

Only immediate files are sorted. Subfolders, symbolic links, and other files are
left alone. Existing images are never intentionally overwritten: duplicate names
get `_1`, `_2`, etc. Back up valuable photos before trying a new release.
On macOS, recognized images with Finder's Locked flag are unlocked before moving.
Concurrent modification of the same files or destination folders by other apps is
not supported; avoid running multiple sorting operations on the same folder.

## Run and test

```sh
python3 image_split.py "/path/to/photos" "/path/to/another folder"
python3 -m unittest discover -s tests -v
```

No third-party Python dependencies are needed. A nonzero exit status means at
least one folder or file failed. Logs go to `~/Library/Logs/image_split.log`,
with console logging as a fallback. `--notify` enables a macOS completion
notification; notification display depends on macOS settings.

## Unsigned macOS installer

ImageSplit bundles Python and installs the Finder Quick Action **Split RAW-JPEG**.

See [installation and manual approval instructions](docs/macos-install.md).

The installer is unsigned and not notarized. Keep macOS security protections enabled.

Candidate 0.1.4 was reported working in a standard account on Apple Silicon, macOS 15.7.4. A fresh-download test on another Apple Silicon Mac remains outstanding. Intel support and the minimum supported macOS version are not yet validated. No public release has been published.

### Build an Apple Silicon candidate

Use a trusted, checksum-verified, relocatable standalone Python 3.10+
runtime and retain its license notices. Do not use a virtual environment
or a symlink to system Python. The builder does not authenticate the runtime.

    python3 packaging/build_installer.py --runtime /path/to/verified/python --arch arm64 --version 0.1.4

Omit --sign for unsigned distribution. The builder checks the interpreter
architecture and smoke-tests the relocated runtime. It writes a package,
SHA-256 checksum, and JSON build record into dist/.

Installation requires administrator authorization. Each user enables
Split RAW-JPEG through Finder > Quick Actions > Customize.

Intel builds require a separately verified x86_64 runtime and --arch x86_64.
They must be tested on an Intel Mac before claiming Intel support.
