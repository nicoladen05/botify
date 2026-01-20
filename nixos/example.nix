{
  # Example NixOS configuration for botify Discord bot
  #
  # To use this module in your NixOS configuration:
  #
  # 1. Add the botify flake to your flake.nix inputs:
  #    inputs.botify.url = "github:yourusername/botify";
  #
  # 2. Import the module in your NixOS configuration:
  #    imports = [ inputs.botify.nixosModules.default ];
  #
  # 3. Add the botify overlay to access the package:
  #    nixpkgs.overlays = [
  #      (final: prev: {
  #        botify = inputs.botify.packages.${final.system}.default;
  #      })
  #    ];

  services.botify = {
    enable = true;

    # Path to a file containing your Discord bot token
    # This file should contain only the token string
    #
    # For agenix users:
    # tokenFile = config.age.secrets.botify-token.path;
    #
    # For sops-nix users:
    # tokenFile = config.sops.secrets.botify-token.path;
    #
    # Or use a plain file (not recommended for production):
    tokenFile = "/run/secrets/botify-token";

    # Optional: Path to a file containing your OpenAI API key
    # If not provided, OpenAI features will be disabled
    #
    # For agenix users:
    # openaiTokenFile = config.age.secrets.openai-api-key.path;
    #
    # For sops-nix users:
    # openaiTokenFile = config.sops.secrets.openai-api-key.path;
    #
    # Or use a plain file (not recommended for production):
    # openaiTokenFile = "/run/secrets/openai-api-key";

    # Optional: Override the package (defaults to pkgs.botify)
    # package = pkgs.botify;

    # Optional: Override the user (defaults to "botify")
    # user = "botify";

    # Optional: Override the group (defaults to "botify")
    # group = "botify";
  };

  # Example: Using with agenix
  # age.secrets.botify-token = {
  #   file = ./secrets/botify-token.age;
  #   owner = "botify";
  #   group = "botify";
  # };
  # age.secrets.openai-api-key = {
  #   file = ./secrets/openai-api-key.age;
  #   owner = "botify";
  #   group = "botify";
  # };

  # Example: Using with sops-nix
  # sops.secrets.botify-token = {
  #   owner = "botify";
  #   group = "botify";
  # };
  # sops.secrets.openai-api-key = {
  #   owner = "botify";
  #   group = "botify";
  # };
}
