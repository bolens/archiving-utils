# Tool catalog

30 commands. Generated from `lib/catalog.json`.

| Command | Category | Mode | Purpose |
|---|---|---|---|
| [`library-inventory`](../util/library/library-inventory/) | library | read | List file sizes and relative paths. |
| [`library-dupes`](../util/library/library-dupes/) | library | read | Find exact SHA-256 duplicates without deleting files. |
| [`hash-manifest`](../util/library/hash-manifest/) | library | read | Print a JSON SHA-256 manifest for the input tree. |
| [`hash-verify`](../util/library/hash-verify/) | library | read | Verify file presence and hashes against a JSON manifest. |
| [`tree-diff`](../util/library/tree-diff/) | library | read | Compare file hashes and presence against another tree. |
| [`path-audit`](../util/library/path-audit/) | library | read | Report filename portability issues. |
| [`folder-to-zip`](../conversion/folder-to-zip/) | conversion | write | Package a directory as zip and verify member hashes. |
| [`archive-to-zip`](../conversion/archive-to-zip/) | conversion | write | Repack a verified archive as zip. |
| [`folder-to-tar`](../conversion/folder-to-tar/) | conversion | write | Package a directory as tar and verify member hashes. |
| [`archive-to-tar`](../conversion/archive-to-tar/) | conversion | write | Repack a verified archive as tar. |
| [`folder-to-tar-gz`](../conversion/folder-to-tar-gz/) | conversion | write | Package a directory as tar.gz and verify member hashes. |
| [`archive-to-tar-gz`](../conversion/archive-to-tar-gz/) | conversion | write | Repack a verified archive as tar.gz. |
| [`folder-to-tar-bz2`](../conversion/folder-to-tar-bz2/) | conversion | write | Package a directory as tar.bz2 and verify member hashes. |
| [`archive-to-tar-bz2`](../conversion/archive-to-tar-bz2/) | conversion | write | Repack a verified archive as tar.bz2. |
| [`folder-to-tar-xz`](../conversion/folder-to-tar-xz/) | conversion | write | Package a directory as tar.xz and verify member hashes. |
| [`archive-to-tar-xz`](../conversion/archive-to-tar-xz/) | conversion | write | Repack a verified archive as tar.xz. |
| [`file-to-gz`](../conversion/file-to-gz/) | conversion | write | Compress individual files with gz and check the round trip. |
| [`gz-to-file`](../conversion/gz-to-file/) | conversion | write | Decompress gz with a bounded output size. |
| [`gz-verify`](../util/audit/gz-verify/) | audit | read | Read and verify the complete gz stream. |
| [`file-to-bz2`](../conversion/file-to-bz2/) | conversion | write | Compress individual files with bz2 and check the round trip. |
| [`bz2-to-file`](../conversion/bz2-to-file/) | conversion | write | Decompress bz2 with a bounded output size. |
| [`bz2-verify`](../util/audit/bz2-verify/) | audit | read | Read and verify the complete bz2 stream. |
| [`file-to-xz`](../conversion/file-to-xz/) | conversion | write | Compress individual files with xz and check the round trip. |
| [`xz-to-file`](../conversion/xz-to-file/) | conversion | write | Decompress xz with a bounded output size. |
| [`xz-verify`](../util/audit/xz-verify/) | audit | read | Read and verify the complete xz stream. |
| [`archive-extract`](../util/archive/archive-extract/) | archive | write | Extract regular files into a new directory after path and size checks. |
| [`archive-list`](../util/audit/archive-list/) | audit | read | List members with sizes and SHA-256 hashes. |
| [`archive-verify`](../util/audit/archive-verify/) | audit | read | Check archive structure, member safety, and complete payloads. |
| [`archive-stats`](../util/audit/archive-stats/) | audit | read | Report member counts, stored size, and expansion ratio. |
| [`archive-manifest`](../util/audit/archive-manifest/) | audit | read | Print member SHA-256 hashes without extraction. |
