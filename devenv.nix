{ pkgs, config, lib, ... }:
let
  developmentHome = pkgs.runCommand "development-home" { } ''
    mkdir -p "$out/env"
  '';
in
{
  name = "archiving-utils";
  # Use existing Nix caches without changing daemon trust configuration.
  cachix.enable = false;
  # This repository has no background services or process-compose configuration.
  process.manager.implementation = "overmind";
  packages = with pkgs; [
    bashInteractive coreutils findutils gawk git gnugrep gnumake gnused
    diffutils python3 shellcheck cacert libarchive zstd binutils stdenv.cc
  ];
  env = { SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"; } // lib.optionalAttrs pkgs.stdenv.isLinux {
    LD_LIBRARY_PATH = lib.makeLibraryPath [ pkgs.libarchive pkgs.zstd ];
  };
  scripts.repo-check.exec = if pkgs.stdenv.isLinux then "make check test-all" else ''
    make check
    python3 -m unittest discover -s tests -p test_comic_headers.py -v
    python3 -m unittest discover -s tests -p test_development_container.py -v
  '';
  enterTest = "repo-check";

  containers.shell = {
    name = "localhost/archiving-utils-dev";
    version = "latest";
    # Mount source when running; never bake checkout files or local secrets in.
    copyToRoot = [ ];
    # Prepare the image's existing home; nothing is mounted here from the host.
    layers = lib.mkAfter [{
      copyToRoot = [ developmentHome ];
      perms = [{ path = developmentHome; regex = "/env"; mode = "1777"; }];
    }];
    entrypoint = [ (pkgs.writeShellScript "development-entrypoint" ''
      export PATH="${lib.makeBinPath config.packages}:$PATH"
      exec "$@"
    '') ];
    startupCommand = "bash";
  };
}
