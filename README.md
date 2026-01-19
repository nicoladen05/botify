# Installation
## Any OS
Install the dependencies.
```bash
pip install -r requirements.txt
```

Create a .env file with your bots token
```bash
echo BOT_TOKEN=[Your Token] > .env
```

## Docker
Build the image.
```bash
docker build . -t botify
```

Run the image normally or through docker-compose. Pass your bot token to the
container using the environment variable `BOT_TOKEN` .

## NixOS
Add the module to your flake inputs:
```nix
{
  inputs = {
    botify.url = "github:yourusername/botify";
  };
}
```

Import the module in your NixOS configuration:
```nix
{
  imports = [ botify.nixosModules.default ];
}
```

Enable and configure the service:
```nix
{
  services.botify = {
    enable = true;
    tokenFile = "/run/secrets/botify-token";
  };
}
```
