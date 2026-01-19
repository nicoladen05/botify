#!/usr/bin/env bash
# Standalone test runner for the botify NixOS module
# This script builds and runs the NixOS VM test

set -euo pipefail

cd "$(dirname "$0")/.."

echo "Building and running NixOS VM test for botify module..."
echo "This will:"
echo "  1. Build the botify package"
echo "  2. Create a NixOS VM with the botify module enabled"
echo "  3. Run automated tests to verify the service works correctly"
echo ""

# Run the test using nix flake check
if command -v nix &> /dev/null; then
    echo "Running test via 'nix flake check'..."
    nix flake check --print-build-logs
    echo ""
    echo "✓ All tests passed!"
    echo ""
    echo "You can also run the test manually with:"
    echo "  nix build .#checks.x86_64-linux.nixos-module"
    echo ""
    echo "Or run it interactively:"
    echo "  nix eval --raw .#checks.x86_64-linux.nixos-module.driverInteractive | sh"
else
    echo "Error: nix command not found. Please ensure Nix is installed."
    exit 1
fi
