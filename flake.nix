{
  description = "Botify";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pycordOverlay = final: prev: rec {
          python313 = prev.python313.override {
            packageOverrides = pythonFinal: pythonPrev: {
              pycord = prev.callPackage ./packages/pycord.nix {};
            };
          };
          python313Packages = python313.pkgs;
        };

        pkgs = import nixpkgs {
          inherit system;
          overlays = [ pycordOverlay ];
        };

        pythonEnv = pkgs.python313.withPackages (ps: with ps; [
          pip
          pycord
          python-dotenv
          pexpect
          aiohttp
          requests
          mcstatus
        ]);
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pythonEnv
          ];
        };
      }
    );
}
