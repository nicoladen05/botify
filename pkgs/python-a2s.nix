{
  buildPythonPackage,
  fetchFromGitHub,
  setuptools,
  setuptools-scm,
  ...
}:

buildPythonPackage {
  pname = "python-a2s";
  version = "1.3.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "Yepoleb";
    repo = "python-a2s";
    rev = "b40eb24cdbb06ebd08272f224257fe5a81610e86";
    hash = "sha256-UGzHpU3ara9fAFhMJHJq5dhttHMC/xColR4fGL3JYmA=";
  };

  build-system = [
    setuptools
    setuptools-scm
  ];

}
