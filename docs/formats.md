# Formats and limits

ZIP and TAR are the package formats. TAR can be uncompressed or compressed with gzip, bzip2, or xz. Standalone stream compression uses gzip, bzip2, and xz. Repacking changes the container, not file contents.

Packing compares SHA-256 member hashes with the source files. Compression compares decompressed SHA-256 with the source. Archive scans read complete payloads and enforce archive checksums where the format provides them. ZIP CRC and compression integrity are not cryptographic authenticity. TAR has no payload checksum, so use a separately trusted SHA-256 manifest for later authenticity checks.

Extraction accepts only relative regular files and directories. It rejects traversal, absolute paths, duplicate members, backslashes, drive-like names, symlinks, hardlinks, devices, and encrypted ZIP entries. Defaults limit expanded bytes to 10 GiB and members to 100,000, configurable with `--max-bytes` and `--max-members`. Files receive normal newly created file permissions. Archive ownership, ACLs, xattrs, sparse layout, and executable permissions are not restored. Repacking likewise preserves file contents and empty directories, not full filesystem metadata. Do not use it as a system backup replacement.

No RAR, 7z, password management, multipart archives, PAR2 repair, signatures, or remote backup transport is implemented. Those features need separate contracts and tests. ZIP metadata parsing can consume memory before member limits are evaluated. Limits do not make the decoder a hostile-input sandbox.
