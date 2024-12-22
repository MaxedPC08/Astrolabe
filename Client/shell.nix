let
  pkgs = import <nixpkgs> {};

in pkgs.mkShell {
  packages = with pkgs; [
    (python312.withPackages (ps: with ps; [
      numpy
      tkinter
    ]))
    python312Packages.pip
  ];
  shellHook = "
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ";
}
