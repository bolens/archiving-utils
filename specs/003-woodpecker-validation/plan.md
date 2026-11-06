# Implementation plan

Use the existing locked `devenv.nix` and `devenv.lock` through the fleet's pinned
Nix image and pinned devenv CLI. Nix sandboxing is disabled only inside the
unprivileged disposable job container; no host daemon settings change.

The existing repository check remains the command authority. GitHub checks stay
available during the first native proof. Validate YAML, source checks, the exact
PR head, and genuine main before changing required check settings or retiring a
hosted lane. Recovery is a corrective or revert PR.

The constitution remains satisfied: disposable fixtures, existing runtime
compatibility, and credential-free validation preserve the current authority.
