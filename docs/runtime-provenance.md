# Apple Silicon runtime provenance

Candidate: ImageSplit 0.1.4, Apple Silicon, unsigned.

Upstream project: astral-sh/python-build-standalone
Release: 20261013
Runtime: CPython 3.13.16
Asset: cpython-3.13.16+20261013-aarch64-apple-darwin-install_only.tar.gz

Release page:
https://github.com/astral-sh/python-build-standalone/releases/tag/20261013

Archive SHA-256, reported by GitHub and verified locally:
ca0e6a70fb75a0984751bd75493e3de77680aef7fbd0fea9b903c299537b3423

On 2026-10-20, the maintainer downloaded the reference archive and verified
its checksum. The installed runtime matched the extracted reference using
diff -qr -x __pycache__, with exit status 0. Bytecode caches were excluded.

Runtime architecture: arm64
Python deployment target: macOS 11.0
Tested host: Apple Silicon, macOS 15.7.4
The deployment target does not establish a tested minimum supported OS.

Candidate package SHA-256:
7107f6f11995b0dc2baf6bf0f93bda66dcff3c31fe2d0fd1d26fadca1f036958

Remaining checks:
- Review bundled license notices and redistribution requirements.
- Test a fresh browser download on another Apple Silicon Mac.
- Establish supported macOS versions.
- Build and validate Intel separately.
