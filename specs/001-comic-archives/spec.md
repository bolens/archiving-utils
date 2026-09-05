# Comic archive support

Branch: `001-comic-archives`. Created: 2026-09-05. Status: implementation.

User request: add extensive comic archive support to archiving-utils.

## User scenarios and acceptance

1. Inspect a comic collection: CBZ/ZIP, CBR/RAR4/RAR5, CB7/7z, CBT/TAR and gzip, bzip2, xz, Zstandard TAR variants produce bounded member hashes and a naturally sorted page inventory. Page recognition is extension-based and does not claim image decoding.
2. Convert containers: each writable comic format accepts every supported input container. All member names, file bytes, sidecars, and empty directories survive. Source archives remain byte-identical. No page is re-encoded or renamed.
3. Build and extract: package a directory into CBZ, CB7, CBT, CBT.GZ, CBT.BZ2, CBT.XZ or CBT.ZST. Extract only into a new directory. Default invocation is a plan; writes require --apply.
4. Refuse unsafe input: traversal, absolute paths, duplicate destinations, links, special files, encrypted entries, incomplete volumes, corruption and expansion limits fail without published partial outputs. Missing optional backends return dependency exit code 2.

## Requirements

- Reuse the catalog, CLI, batch runner, member validation, staging and no-clobber publication.
- Preserve all regular-file sidecars, including ComicInfo.xml, without parsing XML or executing contents. Files without recognized image extensions are retained.
- Report page count, natural filename order, member hashes, metadata-sidecar names and other files. A zero-page archive is reported honestly and remains convertible without silently dropping data.
- Add comic-info, comic-verify, comic-extract, folder-to-* and comic-to-* for the seven writable formats. Generic archive commands also discover comic extensions, .rar, .7z and .tar.zst/.tzst.
- Read RAR only. CBA/ACE, encryption/passwords, multipart assembly, PDF/EPUB rendering, image transcoding, metadata editing, and filesystem metadata restoration are outside this feature. Explicitly reject CBA with a useful error.
- Use standard-library ZIP/TAR codecs where supported. Optional libarchive reads RAR/7z/Zstandard; optional bsdtar writes 7z and Zstandard TAR. No runtime installs or network access.
- Read-only comic commands inherit existing MCP root restrictions. No new write authority.

## Success criteria

Real disposable fixtures exercise every writable format and both RAR generations, cross-format conversion, page ordering, all-member preservation, dry-run, corruption, unsafe members, missing dependencies, batch partial failure and collision refusal. Tests and docs distinguish unavailable backends from passing support. Both supported Python CI versions run the backend-dependent tier.

## Preservation limits

Names and file bytes define the preservation contract. Container-specific comments, original member interleaving, permissions, timestamps, ACLs and xattrs are not retained. Natural page order derives from unchanged names, and individual readers may order differently. Decoder limits bound expanded output, not native decoder memory or CPU.
