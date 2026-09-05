# Implementation plan

Primary agent owns Dockerfile, .dockerignore, Docker test/entrypoint scripts,
Make targets, Docker CI, related documentation and this specification in the
isolated archiving-utils worktree on feat/docker-runtime.

Use the official digest-pinned Debian 13 image with distribution packages.
Copy only runtime source into the image. Existing native checks remain intact.
Run container acceptance through the same Make target locally and in Docker CI.
Follow RELEASING.md with focused commits, independent review and protected merge.
No preservation or authority contract changes are required.
