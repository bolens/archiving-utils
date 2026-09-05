# Formats and limits

ZIP and TAR are the package formats. TAR can be uncompressed or compressed with gzip, bzip2, or xz. Standalone stream compression uses gzip, bzip2, and xz. Repacking changes the container, not file contents.

Packing compares SHA-256 member hashes with the source files. Compression compares decompressed SHA-256 with the source. Archive scans read complete payloads and enforce archive checksums where the format provides them. ZIP CRC and compression integrity are not cryptographic authenticity. TAR has no payload checksum, so use a separately trusted SHA-256 manifest for later authenticity checks.

Extraction accepts only relative regular files and directories. It rejects traversal, absolute paths, duplicate members, backslashes, drive-like names, symlinks, hardlinks, devices, and encrypted ZIP entries. Defaults limit expanded bytes to 10 GiB and members to 100,000, configurable with `--max-bytes` and `--max-members`. Files receive normal newly created file permissions. Archive ownership, ACLs, xattrs, sparse layout, and executable permissions are not restored. Repacking likewise preserves file contents and empty directories, not full filesystem metadata. Do not use it as a system backup replacement.

RAR/7z and comic container support is described below. Password management, multipart assembly, PAR2 repair, signatures and remote backup transport are not implemented. ZIP metadata parsing can consume memory before member limits are evaluated. Limits do not make the decoder a hostile-input sandbox.

## Comic archives

Comic commands package, inspect, extract and convert containers without changing
image data. Names, file bytes, nested folders, empty directories and all sidecars
are preserved. `ComicInfo.xml` is retained byte-for-byte and never parsed as XML.
No image decoding, resizing, metadata editing or page renaming occurs.

| Container | Accepted extensions | Read / extract / convert from | Create / convert to |
|---|---|---|---|
| ZIP | `.cbz`, `.zip` | Yes, standard library | `folder-to-cbz`, `comic-to-cbz` |
| RAR4 / RAR5 | `.cbr`, `.rar` | Yes, optional libarchive | No RAR writer |
| 7z | `.cb7`, `.7z` | Yes, optional libarchive | `folder-to-cb7`, `comic-to-cb7`, optional bsdtar |
| TAR | `.cbt`, `.tar` | Yes, standard library | `folder-to-cbt`, `comic-to-cbt` |
| gzip TAR | `.cbt.gz`, `.tar.gz`, `.tgz` | Yes, standard library | `folder-to-cbt-gz`, `comic-to-cbt-gz` |
| bzip2 TAR | `.cbt.bz2`, `.tar.bz2`, `.tbz2` | Yes, standard library | `folder-to-cbt-bz2`, `comic-to-cbt-bz2` |
| xz TAR | `.cbt.xz`, `.tar.xz`, `.txz` | Yes, standard library | `folder-to-cbt-xz`, `comic-to-cbt-xz` |
| Zstandard TAR | `.cbt.zst`, `.tar.zst`, `.tzst` | Yes, optional native libarchive | `folder-to-cbt-zst`, `comic-to-cbt-zst`, optional bsdtar |
| ACE | `.cba` | Explicitly refused | No |

Extension matching is case-insensitive. Container signatures select the reader,
so a ZIP named `.cbr` is read as ZIP. Use generic archive-list, archive-verify,
archive-manifest or archive-extract with the same extensions. Explicit output
names do not choose the encoding; the command does.

`comic-info` and `comic-verify` read and hash every member and return a page
inventory in natural filename order: `2.jpg` precedes `10.jpg`. Recognized page
suffixes are JPEG (`.jpg`, `.jpeg`, `.jpe`, `.jfif`), PNG/APNG, WebP, GIF,
TIFF (`.tif`, `.tiff`), BMP/DIB, AVIF, HEIC/HEIF, JXL, JPEG 2000
(`.jp2`, `.j2k`, `.jpf`, `.jpx`), PPM/PGM/PBM/PNM and QOI. This classification
uses extensions only. It does not prove an image decodes. A zero-page archive is
reported as such and remains convertible. Unrecognized files are retained.

Comic conversion preserves filename-defined ordering, not the container's
original entry order. Reader sorting rules may differ. ZIP comments, container
metadata, timestamps and filesystem attributes are not preserved. Less common
page encodings and compressed CBT variants may not work in every comic reader.
CBZ with conventional JPEG/PNG pages is the broad-compatibility output choice.

Encryption/passwords, self-extracting executables, multipart assembly, damaged
archive repair, CBA/ACE, and PDF/EPUB rendering are not supported. Missing volumes,
unsafe members and decoder errors fail before publication. Native decoders are
not a hostile-input sandbox: expanded-byte/member limits do not cap their
internal memory or CPU use. Keep libarchive and compression libraries maintained.

RAR5 header CRCs and decoded payload CRC32 are checked independently of
libarchive, including stored entries. This protects against the stored-entry
checksum gap reproduced with libarchive 3.8.9. RAR5 regular files without a
CRC32 field, including BLAKE2-only archives, are explicitly refused. RAR Windows
path separators are normalized by the reader; decoded paths still pass the same
traversal, collision and link restrictions. For all formats, checksums are
integrity checks, not proof of authenticity.
