{
  description = "Botify";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    {
      nixosModules.default = import ./nixos/module.nix;
    }
    // flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python-a2s = pkgs.python313Packages.callPackage ./pkgs/python-a2s.nix { };
        pythonEnv = pkgs.python313.withPackages (
          ps: with ps; [
            discordpy
            python-dotenv
            aiohttp
            requests
            mcstatus
            python-a2s
            rich
            yt-dlp
            openai
          ]
        );
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.ffmpeg
            pkgs.basedpyright
          ];
        };

        packages = {
          default = pkgs.python313Packages.callPackage ./pkgs/default.nix {
            inherit python-a2s;
            inherit (pkgs) ffmpeg;
          };
          python-a2s = python-a2s;
        };

        checks = {
          nixos-module = import ./nixos/test.nix {
            inherit pkgs system self;
          };
        };
      }
    );
}
