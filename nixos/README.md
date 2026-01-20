# Botify NixOS Module

This NixOS module provides a systemd service for running the Botify Discord bot.

## Features

- Systemd service with automatic restarts
- Secure credential management using systemd credentials
- Security hardening (NoNewPrivileges, PrivateTmp, ProtectSystem, ProtectHome)
- Automatic user/group creation
- FFmpeg integration for music playback

## Installation

### Using Flakes

1. Add botify to your flake inputs:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    botify.url = "github:yourusername/botify";
  };

  outputs = { self, nixpkgs, botify, ... }: {
    nixosConfigurations.yourhost = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        botify.nixosModules.default
        
        # Add the package to nixpkgs
        {
          nixpkgs.overlays = [
            (final: prev: {
              botify = botify.packages.${final.system}.default;
            })
          ];
        }
        
        ./configuration.nix
      ];
    };
  };
}
```

2. Configure the service in your `configuration.nix`:

```nix
{
  services.botify = {
    enable = true;
    tokenFile = "/run/secrets/botify-token";
    # Optional: Enable OpenAI features
    # openaiTokenFile = "/run/secrets/openai-api-key";
  };
}
```

## Configuration Options

### `services.botify.enable`

- **Type:** `boolean`
- **Default:** `false`
- **Description:** Whether to enable the Botify Discord bot service.

### `services.botify.tokenFile`

- **Type:** `path`
- **Required:** Yes (when enabled)
- **Description:** Path to a file containing the Discord bot token. This file should contain only the token string.
- **Example:** `"/run/secrets/botify-token"`

### `services.botify.openaiTokenFile`

- **Type:** `path` or `null`
- **Default:** `null`
- **Required:** No
- **Description:** Path to a file containing the OpenAI API key. This file should contain only the API key string. If not provided, OpenAI features will be disabled.
- **Example:** `"/run/secrets/openai-api-key"`

### `services.botify.package`

- **Type:** `package`
- **Default:** `pkgs.botify`
- **Description:** The botify package to use.

### `services.botify.user`

- **Type:** `string`
- **Default:** `"botify"`
- **Description:** User account under which botify runs.

### `services.botify.group`

- **Type:** `string`
- **Default:** `"botify"`
- **Description:** Group under which botify runs.

## Secret Management

### Using agenix

```nix
{
  age.secrets.botify-token = {
    file = ./secrets/botify-token.age;
    owner = "botify";
    group = "botify";
  };

  age.secrets.openai-api-key = {
    file = ./secrets/openai-api-key.age;
    owner = "botify";
    group = "botify";
  };

  services.botify = {
    enable = true;
    tokenFile = config.age.secrets.botify-token.path;
    openaiTokenFile = config.age.secrets.openai-api-key.path;
  };
}
```

### Using sops-nix

```nix
{
  sops.secrets.botify-token = {
    owner = "botify";
    group = "botify";
  };

  sops.secrets.openai-api-key = {
    owner = "botify";
    group = "botify";
  };

  services.botify = {
    enable = true;
    tokenFile = config.sops.secrets.botify-token.path;
    openaiTokenFile = config.sops.secrets.openai-api-key.path;
  };
}
```

### Manual Setup (Not Recommended for Production)

Create files with your Discord bot token and OpenAI API key:

```bash
echo "your-discord-bot-token-here" > /run/secrets/botify-token
chmod 600 /run/secrets/botify-token

# Optional: For OpenAI features
echo "your-openai-api-key-here" > /run/secrets/openai-api-key
chmod 600 /run/secrets/openai-api-key
```

## Service Management

### Check service status

```bash
systemctl status botify
```

### View logs

```bash
journalctl -u botify -f
```

### Restart service

```bash
systemctl restart botify
```

### Stop service

```bash
systemctl stop botify
```

## Security Features

The module includes several security hardening measures:

- **NoNewPrivileges:** Prevents privilege escalation
- **PrivateTmp:** Uses a private /tmp directory
- **ProtectSystem:** Makes system directories read-only
- **ProtectHome:** Makes /home inaccessible
- **LoadCredential:** Securely loads the bot token without exposing it in the process list

## Troubleshooting

### Bot doesn't start

1. Check the service logs:
   ```bash
   journalctl -u botify -n 50
   ```

2. Verify the token file exists and is readable:
   ```bash
   ls -la /run/secrets/botify-token
   ```

3. Check the token file contents (ensure it's just the token, no extra whitespace):
   ```bash
   cat /run/secrets/botify-token | wc -c
   ```

### Permission denied errors

Ensure the token file is readable by the botify user:
```bash
chown botify:botify /run/secrets/botify-token
chmod 400 /run/secrets/botify-token
```

### Bot crashes frequently

Check if all required dependencies are available. The service will automatically restart after 10 seconds on failure.

## Testing

The module includes automated tests that verify the service works correctly in a NixOS VM.

### Running Tests

Run all tests using nix flake check:

```bash
nix flake check --print-build-logs
```

Or use the provided test runner script:

```bash
./nixos/run-test.sh
```

### Running Tests Manually

Build the test:

```bash
nix build .#checks.x86_64-linux.nixos-module
```

Run the test interactively (opens a VM):

```bash
nix eval --raw .#checks.x86_64-linux.nixos-module.driverInteractive | sh
```

### What the Tests Verify

The automated tests check:

- ✓ Botify package builds successfully
- ✓ NixOS module loads without errors
- ✓ Service user and group are created
- ✓ Systemd service unit is properly configured
- ✓ Service can start (with dummy token)
- ✓ Security hardening options are applied
- ✓ FFmpeg is available in the service PATH
- ✓ Credentials are loaded correctly
- ✓ Service runs as the correct user/group

### Test Implementation

The test is defined in [test.nix](./test.nix) and creates a minimal NixOS VM with the botify service enabled. It uses a dummy token for testing purposes, so the bot won't actually connect to Discord, but it verifies that all the systemd service configuration is correct.

## Complete Example

See [example.nix](./example.nix) for a complete configuration example.
