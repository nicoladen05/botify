# Testing the Botify NixOS Module

Quick reference for running the automated NixOS VM tests.

## Quick Start

```bash
# Run all tests (recommended)
nix flake check --print-build-logs

# Or use the test runner script
./nixos/run-test.sh
```

## Test Commands

### Basic Testing

```bash
# Run all flake checks (includes module test)
nix flake check

# With detailed build logs
nix flake check --print-build-logs

# Build test derivation directly
nix build .#checks.x86_64-linux.nixos-module

# Run with verbose output
nix build .#checks.x86_64-linux.nixos-module -L
```

### Interactive Testing

```bash
# Launch interactive test VM
nix eval --raw .#checks.x86_64-linux.nixos-module.driverInteractive | sh

# Inside the VM, you can:
# - Check service status: systemctl status botify
# - View logs: journalctl -u botify -f
# - Inspect configuration: systemctl cat botify.service
# - Check user: id botify
```

### Debugging

```bash
# Show test script without running
nix eval .#checks.x86_64-linux.nixos-module.testScript

# Build and inspect test driver
nix build .#checks.x86_64-linux.nixos-module.driver
./result/bin/nixos-test-driver

# View full build logs after failure
nix log /nix/store/...-vm-test-run-botify-module-test.drv
```

## What the Tests Verify

✅ Package builds successfully  
✅ Module loads without errors  
✅ System user and group created  
✅ Systemd service configured correctly  
✅ Service can start  
✅ Binary is executable  
✅ FFmpeg is in PATH  
✅ Security hardening applied  
✅ Runs as correct user/group  
✅ Credentials loaded via systemd  

## Expected Behavior

The test service will:
1. ✅ Start successfully
2. ✅ Load the dummy token
3. ✅ Attempt to connect to Discord
4. ❌ Fail authentication (expected with dummy token)
5. ✅ Exit with code 1

This is **correct behavior** - it proves all systemd configuration works!

## Test Duration

- Full test run: ~100-120 seconds
- VM boot time: ~50 seconds
- Test execution: ~50-70 seconds

## Requirements

- Nix with flakes enabled
- KVM support (optional but recommended for speed)
- ~2GB RAM available
- ~5GB disk space for build cache

## Common Issues

### Files not tracked by Git

```bash
error: Path 'nixos/test.nix' is not tracked by Git.
```

**Solution:**
```bash
git add nixos/test.nix
```

### Insufficient Memory

```bash
error: VM failed to start
```

**Solution:** Increase available RAM or close other applications

### KVM Not Available

The test will run slower without KVM but still works. To check:

```bash
ls /dev/kvm  # Should exist for KVM support
```

## Continuous Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run NixOS Module Tests
  run: nix flake check --print-build-logs
```

For Hydra/Hercules CI, the test is automatically included in the flake's checks output.

## Files

- `test.nix` - Test implementation
- `run-test.sh` - Convenience script
- `TEST-RESULTS.md` - Detailed test documentation
- `README.md` - Full module documentation

## More Information

See [TEST-RESULTS.md](./TEST-RESULTS.md) for detailed test results and coverage information.