# RAR regression fixtures

The `.uu` files are unmodified libarchive test fixtures from commit
`b439d586f53911c84be5e380445a8a259e19114c` (v3.7.7), under
`libarchive/test/` in the [upstream repository](https://github.com/libarchive/libarchive/tree/b439d586f53911c84be5e380445a8a259e19114c/libarchive/test).
See `COPYING` and `TEST-LICENSES` for retained notices.

Tests decode these text fixtures into disposable `.cbr` files, offline.
`expected.json` records SHA-256 payloads obtained independently with bsdtar
3.8.9, plus directory entries. Positive fixtures exercise RAR4 and stored and
compressed RAR5. Their contents are upstream test text/binary data, not comic
artwork; comic-info honestly reports zero recognized pages. The `.lnk` file is
retained as opaque bytes and never executed. Other fixtures exercise encryption,
symlinks, hardlinks and a missing next volume. No fixture contents are executed.
