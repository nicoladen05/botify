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
  openai,
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
    openai
  ];

  passthru = {
    inherit python-a2s ffmpeg;
  };
}
