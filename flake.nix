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
    flake-utils.lib.eachDefaultSystem (
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
          default = pkgs.python313Packages.callPackage ./pkgs/default.nix { };
          python-a2s = python-a2s;
        };
      }
    );
}
