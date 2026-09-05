# archiving-utils

[![CI](https://github.com/bolens/archiving-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/bolens/archiving-utils/actions/workflows/ci.yml)

Package, inspect, compare, and recover local archives. Every compression pipeline checks the round trip before publishing its output.

**[Browse the site](https://bolens.github.io/archiving-utils/)** · [Command catalog](docs/catalog.md) · [Architecture diagram](https://bolens.github.io/archiving-utils/diagrams/architecture.html)

## Start here

GNU/Linux, Bash 4.3+, and Python 3.11+. See [requirements](docs/requirements.md) for operation-specific dependencies.

```bash
git clone https://github.com/bolens/archiving-utils.git
cd archiving-utils
bin/archiving-utils list
bin/archiving-utils folder-to-tar-xz --output collection.tar.xz ./collection
# Review the plan, then add --apply to create outputs.
```

31 commands cover conversion, inspection, and library maintenance. Tool directories are thin Bash entry points over a shared Python engine, following the layout and preservation intent of [audio-utils](https://github.com/bolens/audio-utils).

## Working contract

- Writes require `--apply`. `--dry-run` suppresses writes, including report files.
- Sources are retained. Outputs are verified in a temporary directory and published without overwriting existing destinations.
- Inputs can be files or recursive directory trees. Input symlinks are not followed. Filenames travel as arguments, never shell code.
- JSON results go to stdout. Progress and failures go to stderr. Exit codes are 0 success, 1 operation failure, 2 usage or dependency failure.
- `-j 1..32` controls batch concurrency. `--output-dir` preserves relative paths and appends the output suffix to the complete source name.
- The stdio MCP server exposes only read-only tools under explicitly allowed roots.

## Development

```bash
make check
make test
make test-functional
make test-all
make generate
make install-hooks
make -C conversion/folder-to-tar-xz help
```

[CLI and configuration](docs/cli.md) · [Formats and limits](docs/formats.md) · [Architecture](docs/architecture.md) · [MCP](docs/mcp.md) · [Tests](tests/README.md) · [Release procedure](docs/releasing.md) · [Contributing](CONTRIBUTING.md)

## Status

Initial 0.1.0 implementation. This is a sibling suite, not a claim of identical feature maturity or codec coverage to audio-utils. The [parity notes](docs/parity.md) explain the implemented conventions and deliberate differences.

[MIT license](LICENSE). External encoders keep their own licenses.
