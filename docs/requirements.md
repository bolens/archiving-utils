# Requirements

GNU/Linux, Bash 4.3+, Python 3.11+, and GNU Make for development shortcuts. No third-party Python packages are used. Python 3.11 and 3.14 run in CI. ShellCheck is required for `make check`.

Archive operations use Python standard-library ZIP, TAR, gzip, bz2, and lzma modules. Python must include zlib, bz2, and lzma support. Directory publication requires glibc with `renameat2`, available on supported GNU/Linux systems. No 7-Zip, RAR, encryption, or network service is required. CI installs only Python, Make, and ShellCheck; it does not download media encoders.

Local Arch Linux development has the media tools available. Debian/Ubuntu users can install Python, Make, ShellCheck, and FFmpeg from distribution packages. Ubuntu 24.04 ships ImageMagick 6, so image CI builds the pinned ImageMagick 7 release shown in its workflow. The CI build is a disposable runner operation, not a user-machine installer.

External media parsers process local files. This is not a sandbox for malicious media. Keep the operating system, codecs, and ImageMagick security policy maintained. Image tools accept the listed raster extensions and stage literal filenames before calling ImageMagick. Video input protocols and demuxers are restricted to supported local formats.

No automatic downloads, network enrichment, telemetry, package installation, or source deletion happens when running commands.
