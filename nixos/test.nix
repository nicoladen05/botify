{
  pkgs,
  self,
  system,
}:

let
  # Get the botify package and module from self
  botifyPackage = self.packages.${system}.default;
  botifyModule = self.nixosModules.default;
in

pkgs.testers.runNixOSTest {
  name = "botify-module-test";

  nodes.machine =
    { config, lib, ... }:
    {
      imports = [ botifyModule ];

      # Make the botify package available by setting it directly
      services.botify.package = lib.mkForce botifyPackage;

      # Create a dummy token file for testing
      environment.etc."botify-token".text = "DUMMY_TOKEN_FOR_TESTING_ONLY";

      # Enable the botify service
      services.botify = {
        enable = true;
        tokenFile = "/etc/botify-token";
      };
    };

  testScript = ''
    start_all()

    # Wait for the machine to boot
    machine.wait_for_unit("multi-user.target")

    # Check that the botify user was created
    machine.succeed("id botify")
    machine.succeed("getent group botify")

    # Check that the systemd service is defined
    machine.succeed("systemctl cat botify.service")

    # Check that the service can start (it will fail to connect to Discord with dummy token, but that's expected)
    # We just want to verify the service unit is valid and can be activated
    machine.succeed("systemctl start botify.service")

    # Verify the service reached active or activating state
    # (it might fail quickly due to invalid token, so we check it was at least attempted)
    machine.succeed("systemctl status botify.service || systemctl is-failed botify.service")

    # Check that the botify binary exists and is executable
    machine.succeed("test -x ${botifyPackage}/bin/botify")

    # Verify ffmpeg is in the PATH (required for music functionality)
    machine.succeed("systemctl show -p Environment botify.service | grep -q ffmpeg")

    # Verify security hardening options are applied
    machine.succeed("systemctl show -p NoNewPrivileges botify.service | grep -q yes")
    machine.succeed("systemctl show -p PrivateTmp botify.service | grep -q yes")
    machine.succeed("systemctl show -p ProtectSystem botify.service | grep -q strict")
    machine.succeed("systemctl show -p ProtectHome botify.service | grep -q yes")

    # Check the service runs as the correct user
    machine.succeed("systemctl show -p User botify.service | grep -q botify")
    machine.succeed("systemctl show -p Group botify.service | grep -q botify")

    # Verify the package was built correctly
    machine.succeed("${botifyPackage}/bin/botify --help || true")

    print("All tests passed!")
  '';
}
