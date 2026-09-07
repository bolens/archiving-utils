# Development environments

[Documentation](README.md)

Install [Nix and devenv](https://devenv.sh/getting-started/), then run from this checkout:

```sh
devenv shell
repo-check
# Or run the same portable gate non-interactively:
devenv test
```

The shell supplies Python, libarchive/bsdtar, Zstandard, Bash, Git, Make, ShellCheck, and GNU utilities. `repo-check` runs the full `make check test-all` gate on Linux, including generated documentation, managed-tool integrity, CLI/MCP behavior, and real archive round trips on disposable fixtures. The environment exposes the pinned libarchive and Zstandard libraries to Python. On native macOS it runs repository validation, dependency-free comic header tests, and container-adapter tests; full directory publication requires Linux glibc `renameat2`. Run the full suite in a Linux container. The unittest output reports unavailable native archive backends. See [requirements.md](requirements.md) and [../tests/README.md](../tests/README.md) for the format and preservation contracts.

Commit `devenv.lock` with deliberate input updates. Local state and `devenv.local.nix` / `devenv.local.yaml` overrides are ignored. Existing Nix cache settings are used without changing daemon trust.

## Docker and Podman

Build and load the development image, then run a command with a local engine:

```sh
python3 scripts/development-container.py build podman
python3 scripts/development-container.py run podman -- make check test-all
# Substitute docker for podman to use Docker.
```

Omit the command for an interactive Bash shell. The helper mounts the checkout at `/workspace`, runs with the caller's UID/GID, and uses Podman's keep-id mapping. It forwards arguments and exit status without constructing a shell command. These mounts require a local engine with access to the checkout path; remote Docker daemons need their own source transfer. Paths containing commas are rejected because they cannot be represented by this mount syntax.

The image contains tools, not checkout files. Build archives live under `.devenv/containers/` and are never uploaded by the helper. Existing production images and Compose stacks are separate from this development image.

## Apple container

[Apple container](https://github.com/apple/container) requires a supported Apple-silicon Mac. Start its runtime according to Apple's installation guide. With a Linux Nix builder configured:

```sh
python3 scripts/development-container.py build apple
python3 scripts/development-container.py run apple -- make check test-all
```

The helper exports an OCI archive and uses `container image load`. Native ARM Macs target `aarch64-linux`; x86 Linux builds target `x86_64-linux`. [Building Linux images from macOS requires a Linux builder](https://devenv.sh/containers/). This workflow does not assume Apple container implements Docker Compose or Docker's daemon API.

Apple execution is not verified by Linux tests. The product targets GNU/Linux. Native macOS checks exercise the development toolset; use a Linux container for Linux runtime behavior. Linux glibc directory publication and native archive backends determine functional coverage. Tests use disposable generated media and retain sources.
