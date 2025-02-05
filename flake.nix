{
  description = "Botify";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonEnv = pkgs.python313.withPackages (ps: with ps; [
          virtualenv
          pip
        ]);
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.ffmpeg
          ];
          shellHook = ''
            virtualenv venv
            source venv/bin/activate
            pip install -r requirements.txt
            # Reinstall the actual pycord
            pip uninstall py-cord -y
            pip install py-cord
          '';
        };
      }
    );
}
