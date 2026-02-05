{
  buildPythonPackage,
  fetchFromGitHub,
  setuptools,
  setuptools-scm,
  psycopg,
  psycopg-pool,
  pydantic,
  fetchpatch,
  ...
}:

buildPythonPackage {
  pname = "embar";
  version = "1.3.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "carderne";
    repo = "embar";
    rev = "966846eafe84700624d349ba5fa5d811aab8038c";
    hash = "sha256-hhS9Olay1Kg/BXL2ELkF52dTcddmqYfLghZJ6wCKkUc=";
  };

  build-system = [
    setuptools
    setuptools-scm
  ];

  dependencies = [
    psycopg
    psycopg-pool
    (pydantic.overridePythonAttrs (oldAttrs: {
      PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1;

      patches = [
        (fetchpatch {
          url = "https://github.com/pydantic/pydantic/commit/53cb5f830207dd417d20e0e55aab2e6764f0d6fc.patch";
          hash = "sha256-Y1Ob1Ei0rrw0ua+0F5L2iE2r2RdpI9DI2xuiu9pLr5Y=";
        })
      ];
    }))
  ];
}
