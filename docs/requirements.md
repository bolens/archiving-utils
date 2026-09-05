# Requirements

GNU/Linux, Bash 4.3+, Python 3.11+, and GNU Make for development shortcuts. No third-party Python packages are used. Python 3.11 and 3.14 run in CI. ShellCheck is required for `make check`.

Archive operations use Python standard-library ZIP, TAR, gzip, bz2, and lzma modules. Python must include zlib, bz2, and lzma support. Directory publication requires glibc with `renameat2`, available on supported GNU/Linux systems. No 7-Zip, RAR, encryption, or network service is required. CI installs only Python, Make, and ShellCheck; it does not download media encoders.

Development checks need Python, Make, and ShellCheck. Archive operations do not require FFmpeg or ImageMagick.

Archive parsers process local files. Keep Python and its compression libraries maintained. Extraction rejects unsafe member paths and links and enforces the byte and member limits described in [Formats and limits](formats.md).

No automatic downloads, network enrichment, telemetry, package installation, or source deletion happens when running commands.

## Development checkouts

The checkout folder may be renamed or contain spaces and Unicode. CLI identity
and the default configuration directory remain `archiving-utils`. Git is required
for the disposable-checkout regression tests; normal media commands do not
require Git. Tests copy only tracked source and isolate HOME/XDG/TMPDIR state.
