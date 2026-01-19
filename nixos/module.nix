{
  config,
  lib,
  pkgs,
  ...
}:

let
  cfg = config.services.botify;
in
{
  options.services.botify = {
    enable = lib.mkEnableOption "Botify Discord bot";

    tokenFile = lib.mkOption {
      type = lib.types.path;
      description = lib.mdDoc ''
        Path to a file containing the Discord bot token.
        This file should contain only the token string.
      '';
      example = "/run/secrets/botify-token";
    };

    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.botify or (throw "botify package not found in pkgs");
      defaultText = lib.literalExpression "pkgs.botify";
      description = lib.mdDoc ''
        The botify package to use.
      '';
    };

    user = lib.mkOption {
      type = lib.types.str;
      default = "botify";
      description = lib.mdDoc ''
        User account under which botify runs.
      '';
    };

    group = lib.mkOption {
      type = lib.types.str;
      default = "botify";
      description = lib.mdDoc ''
        Group under which botify runs.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.botify = {
      description = "Botify Discord Bot";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];

      serviceConfig = {
        Type = "simple";
        User = cfg.user;
        Group = cfg.group;
        Restart = "on-failure";
        RestartSec = "10s";

        # Security hardening
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = true;

        # Load the bot token from file
        LoadCredential = "bot-token:${cfg.tokenFile}";

        # Set environment variables
        Environment = [
          "PYTHONUNBUFFERED=1"
          "PATH=${lib.makeBinPath [ cfg.package.passthru.ffmpeg ]}"
          "TOKEN_PATH=${cfg.tokenFile}"
        ];

        WorkingDirectory = "${cfg.package}/${pkgs.python313.sitePackages}";
      };

      # Set BOT_TOKEN environment variable from the credential file and run the bot
      script = ''
        BOT_TOKEN=$(cat $TOKEN_PATH) bash ${cfg.package}/bin/botify
      '';
    };

    users.users = lib.mkIf (cfg.user == "botify") {
      botify = {
        isSystemUser = true;
        group = cfg.group;
        description = "Botify Discord bot user";
      };
    };

    users.groups = lib.mkIf (cfg.group == "botify") {
      botify = { };
    };
  };
}
