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
        lavalinkpy = pkgs.python313.pkgs.callPackage ./packages/lavalinkpy.nix { };
        pythonEnv = pkgs.python313.withPackages (
          ps: with ps; [
            discordpy
            python-dotenv
            lavalinkpy
            aiohttp
            requests
            mcstatus
            rich
          ]
        );
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.ffmpeg
          ];
        };

        packages = {
          lavalinkpy = lavalinkpy;
        };
      }
    );
}
