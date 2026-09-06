# Requirements

[Documentation](README.md)

GNU/Linux, Bash 4.3+, Python 3.11+, and GNU Make for development shortcuts. No third-party Python packages are used. Python 3.11 and 3.14 run in CI. ShellCheck is required for `make check`.

Archive operations use Python standard-library ZIP, TAR, gzip, bz2, and lzma modules. Python must include zlib, bz2, and lzma support. Directory publication requires glibc with `renameat2`, available on supported GNU/Linux systems. The original ZIP/TAR/stream commands need no external archive tool. Comic RAR/7z/Zstandard support additionally uses libarchive; writing CB7 and Zstandard CBT uses bsdtar. CI installs libarchive-tools so native format tests run on both Python versions.

Development checks need Python, Make, and ShellCheck. Archive operations do not require FFmpeg or ImageMagick.

Archive parsers process local files. Keep Python and its compression libraries maintained. Extraction rejects unsafe member paths and links and enforces the byte and member limits described in [Formats and limits](formats.md).

No automatic downloads, network enrichment, telemetry, package installation, or source deletion happens when running commands.

## Development checkouts

The checkout folder may be renamed or contain spaces and Unicode. CLI identity
and the default configuration directory remain `archiving-utils`. Git is required
for the disposable-checkout regression tests; normal media commands do not
require Git. Tests copy only tracked source and isolate HOME/XDG/TMPDIR state.

## Optional comic archive backend

Install your distribution's maintained libarchive shared library and bsdtar for
CBR/RAR, CB7/7z and Zstandard TAR. Debian/Ubuntu provide `libarchive-tools` with
the required shared-library dependency; Arch provides both through `libarchive`.
No third-party Python package, proprietary RAR writer or 7z executable is needed.
Missing backends return exit code 2 only when an operation needs them. Planning
and standard ZIP/TAR operations remain available without them. Builds need native
7z/RAR/RAR5 and Zstandard support. Decoder warnings and unavailable compression
features fail explicitly rather than silently omitting members.

## Docker

The [Docker guide](docker.md) describes the packaged runtime and its limits.
