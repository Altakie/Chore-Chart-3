let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
  pkgs = import nixpkgs {
    config = { };
    overlays = [ ];
  };
in
pkgs.mkShellNoCC {
  packages = with pkgs; [
    uv
    ruff
    python313
    # python313Packages.python-lsp-server
    # python313Packages.python-lsp-black
    # python313Packages.ufmt
    # python313Packages.python-dotenv
    # python313Packages.hikari
    # python313Packages.hikari-lightbulb
  ];
}
