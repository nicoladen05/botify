{
  buildPythonPackage,
  fetchFromGitHub,
  setuptools,
  setuptools-scm,
  aiohttp,
}:

buildPythonPackage rec {
  pname = "lavalinkpy";
  version = "5.9.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "devoxin";
    repo = "lavalink.py";
    rev = version;
    hash = "sha256-+tIQz+P4qqGTb/uzvi1BF3pe198g44g+D72XrIondXk=";
  };

  build-system = [
    setuptools
    setuptools-scm
  ];

  dependencies = [
    aiohttp
  ];
}
