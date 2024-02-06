rec {
  shellHook-for = { package, python, nixpkgsRelease }: ''
    export PNAME="${package.pname}";
    export PVERSION="${package.version}";
    export PYVERSION="${python.name}";
    export NIXPKGSRELEASE="${nixpkgsRelease}";
    export PS1="\033[37m[\[\033[01;33m\]\$PNAME-\$PVERSION\033[01;37m|\033[01;32m\]\$PYVERSION\]\033[37m|\[\033[00m\]\[\033[01;34m\]\W\033[37m]\033[31m\$\[\033[00m\] ";
    echo;
    echo -e "        _           \033[34m__ _       _\033[0m";
    echo -e "       (_)         \033[34m/ _| |     | |\033[0m       GPLv3";
    echo -e "  \033[32m_ __  ___  __\033[37m   \033[34m| |_| | __ _| | _____  ___\033[0m";
    echo -e " \033[32m| '_ \\| \\ \\/ /   \033[34m|  _| |/ _\` | |/ / _ \\/ __| \\033[32mhttps://github.com/nixos/nixpkgs/$NIXPKGSRELEASE\033[0m";
    echo -e " \033[32m| | | | |>  < \033[2m\033[46m   \033[0m\033[34m| | | | (_| |   <  __/\\__ \\ \033[36mhttps://github.com/rydnr/nix-flakes\033[0m";
    echo -e " \033[32m|_| |_|_/_/\\_\   \033[34m|_| |_|\__,_|_|\\_\\___||___/ https://patreon.com/rydnr\033[0m";
    echo;
    echo " Thank you for making Nix and rydnr's Nix Flakes your choice, and for your appreciation of free software.";
    echo;
  '';
  devShell-for = { package, python, pkgs, nixpkgsRelease }:
    pkgs.mkShell {
      buildInputs = [ package ];
      shellHook = shellHook-for { inherit package python nixpkgsRelease; };
    };
  app-for = { package, entrypoint }: {
    type = "app";
    program = "${package}/bin/${entrypoint}";
  };
}
