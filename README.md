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

## Build the macOS installer prototype

The installer sources are included; a downloadable release is not built yet.
Build on macOS using a **trusted, relocatable, standalone Python 3.10+ runtime**
containing `bin/python3` and its standard library. A virtual environment or a
symlink to system Python is not a standalone runtime. Use an upstream macOS
standalone distribution, verify its published checksum/signature, retain its
license notices, and select an architecture and minimum macOS version matching
your release. The builder does not download or authenticate runtime artifacts.
Publish separate Apple Silicon and Intel packages unless the runtime is universal.

```sh
python3 packaging/build_installer.py --runtime /path/to/verified/standalone/python
```

The builder copies and smoke-tests the runtime after relocation, generates the
Automator workflow, and produces `dist/ImageSplit.pkg`. It installs:

- `/Library/Application Support/ImageSplit/image_split.py`
- `/Library/Application Support/ImageSplit/runtime/`
- `/Library/Services/Split RAW-JPEG.workflow`

The package requires administrator approval and makes the Quick Action available
to all users. It bundles its own Python and does not install a system Python.
In Finder, select one or more folders and choose **Quick Actions → Split RAW/JPEG**.
If needed, enable it in macOS Settings under Extensions / Finder or Services
(the location varies by macOS version), then reopen Finder. macOS may request
access to protected folders or external drives; grant access only as needed.

### Required macOS release checks

The Linux development environment can validate sorting but cannot validate
`pkgbuild`, Automator registration, macOS file flags, permissions, or Gatekeeper.
On a clean Mac for each supported architecture and macOS version:

1. Build and install the package without relying on a preinstalled Python.
2. Select folders with spaces, apostrophes, and Unicode names, including multiple
   selections. Confirm RAW/JPEG contents, collision handling, and repeat runs.
3. Try locked images, a read-only folder, and external-drive photos. Verify errors
   appear in the log and a completion notification reports failures.
4. Reinstall/upgrade and confirm the Quick Action still works after logging out.

For public distribution, sign bundled executable code as required by Apple's
current notarization rules, then build with
`--sign "Developer ID Installer: Your Name (TEAMID)"`. Submit the resulting package
with `xcrun notarytool submit dist/ImageSplit.pkg --keychain-profile PROFILE --wait`,
staple it using `xcrun stapler staple dist/ImageSplit.pkg`, and validate with
`xcrun stapler validate` and `spctl --assess --type install --verbose` on the package.
An installer signature alone does not sign its bundled runtime. Keep signing
credentials out of this repository. Upload the validated package and SHA-256
checksum to GitHub Releases, then link that release from the website.

To uninstall, remove the three ImageSplit paths listed above using administrator
permissions. Your photos and per-user log files remain untouched.
