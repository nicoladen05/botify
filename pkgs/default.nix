{
  buildPythonApplication,
  setuptools,
  discordpy,
  python-dotenv,
  aiohttp,
  requests,
  mcstatus,
  python-a2s,
  rich,
  yt-dlp,
  ffmpeg,
  ...
}:

buildPythonApplication {
  pname = "botify";
  version = "1.0.0";
  pyproject = true;

  src = ../.;

  build-system = [ setuptools ];

  dependencies = [
    discordpy
    python-dotenv
    aiohttp
    requests
    mcstatus
    python-a2s
    rich
    yt-dlp
  ];

  passthru = {
    inherit python-a2s ffmpeg;
  };
}
