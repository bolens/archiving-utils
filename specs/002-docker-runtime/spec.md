# Docker runtime for archiving-utils

Provide a locally buildable Linux CLI image with the existing tool contracts.
Use a non-root default, support an explicit caller UID/GID, and operate offline
on bind-mounted disposable media. Preserve arguments, exit codes, sources and
existing output policy. Support a read-only root filesystem with writable /tmp.
Install runtime dependencies at build time only. Publish tested main images to GHCR with commit and latest tags. No
version bump, daemon service, host permission changes or automatic device access.

Acceptance: build the image, run help and invalid-command handling, perform a
real conversion, verify its output and retained source, and test unusual names,
read-only input mounts, output ownership and failed/colliding operations.
Document optional dependencies and device/network operations honestly.
