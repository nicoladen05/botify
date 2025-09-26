{ 
  python313Packages,
  fetchFromGitHub,
  voiceSupport ? false
}:

python313Packages.buildPythonPackage {
  pname = "pycord";
  version = "2.7.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "Pycord-Development";
    repo = "pycord";
    rev = "3b8b79f2040caa1bd4130fd4b01cde688e496261";
    sha256 = "sha256-CB7qAMjLazGRIH1idgvY3pRWCwbOeibgNtK4k3SgWVc=";
  };

  build-system = with python313Packages; [ 
    setuptools
    setuptools-scm
  ];

  dependencies = with python313Packages; [
    aiohttp
    typing-extensions
  ] ++ lib.optionals voiceSupport [pynacl];

  postPatch = ''
    substituteInPlace pyproject.toml \
      --replace-fail 'setuptools>=62.6,<=80.9.0' 'setuptools>=62.6' \
      --replace-fail 'setuptools-scm>=6.2,<=9.2.0' 'setuptools-scm>=6.2' \
      --replace-fail 'license = "MIT"' 'license = { file = "LICENSE" }' \
      --replace-fail 'license-files = ["LICENSE"]' '# removed'
  '';
}
