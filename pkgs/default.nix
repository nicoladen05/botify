{
  buildPythonApplication,
  ...
}:

buildPythonApplication {
  pname = "botify";
  version = "1.0.0";
  pyproject = true;

  src = ../.;
}
