# nix/flake.nix
#
# This file packages dvcoolarun/web2pdf as a Nix flake.
#
# Copyright (C) 2024-today rydnr's rydnr/web2pdf fork
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
{
  description = "CLI to convert webpages to PDFs";

  inputs = rec {
    flake-utils.url = "github:numtide/flake-utils/v1.0.0";
    flit = {
      inputs.flake-utils.follows = "flake-utils";
      inputs.nixos.follows = "nixos";
      url = "github:rydnr/nix-flakes/flit-3.9.0-0?dir=flit";
    };
    nixos.url = "github:NixOS/nixpkgs/23.05";
  };
  outputs = inputs:
    with inputs;
    let
      defaultSystems = flake-utils.lib.defaultSystems;
      supportedSystems = if builtins.elem "armv6l-linux" defaultSystems then
        defaultSystems
      else
        defaultSystems ++ [ "armv6l-linux" ];
    in flake-utils.lib.eachSystem supportedSystems (system:
      let
        owner = "dvcoolarun";
        repo = "web2pdf";
        version = "0.0.0";
        pname = "${owner}-${repo}";
        description = "CLI to convert webpages to PDFs";
        homepage = "https://github.com/${owner}/${repo}";
        maintainers = [ "dvcoolarun" ];
        nixosVersion = builtins.readFile "${nixos}/.version";
        nixpkgsRelease =
          builtins.replaceStrings [ "\n" ] [ "" ] "nixos-${nixosVersion}";
        pkgs = import nixos { inherit system; };
        shared = import ./shared.nix;
        pnameWithUnderscores = builtins.replaceStrings [ "-" ] [ "_" ] pname;
        dvcoolarun-web2pdf-for = { flit, python }:
          let
            pythonVersionParts = builtins.splitVersion python.version;
            pythonMajorVersion = builtins.head pythonVersionParts;
            pythonMajorMinorVersion =
              "${pythonMajorVersion}.${builtins.elemAt pythonVersionParts 1}";
            pythonPackage = pnameWithUnderscores;
          in python.pkgs.buildPythonPackage rec {
            inherit pname version;
            pyprojectTemplateFile = ./pyprojecttoml.template;
            pyprojectTemplate = pkgs.substituteAll {
              authors = builtins.concatStringsSep ","
                (map (item: ''"${item}"'') maintainers);
              desc = description;
              inherit homepage pname pythonMajorMinorVersion version;
              dominate = python.pkgs.dominate.pname;
              dominateVersion = python.pkgs.dominate.version;
              fakeUseragent = python.pkgs.fake-useragent.pname;
              fakeUseragentVersion = python.pkgs.fake-useragent.version;
              flit = flit.pname;
              flitVersion = flit.version;
              grequests = python.pkgs.grequests.pname;
              grequestsVersion = python.pkgs.grequests.version;
              package = pnameWithUnderscores;
              pillow = python.pkgs.pillow.pname;
              pillowVersion = python.pkgs.pillow.version;
              readabilityLxml = python.pkgs.readability-lxml.pname;
              readabilityLxmlVersion = python.pkgs.readability-lxml.version;
              rich = python.pkgs.rich.pname;
              richVersion = python.pkgs.rich.version;
              src = pyprojectTemplateFile;
              typer = python.pkgs.typer.pname;
              typerVersion = python.pkgs.typer.version;
              validators = python.pkgs.validators.pname;
              validatorsVersion = python.pkgs.validators.version;
              weasyprint = python.pkgs.weasyprint.pname;
              weasyprintVersion = python.pkgs.weasyprint.version;
            };

            src = pkgs.fetchFromGitHub {
              inherit owner repo;
              rev = "main";
              sha256 = "sha256-XlRPLNSxteFj88gbiWLyPX6FiPrEc2XjCl9xsEO5m8E=";
            };
            format = "pyproject";

            doCheck = false;

            nativeBuildInputs = with python.pkgs; [ pip poetry-core ];
            propagatedBuildInputs = with python.pkgs; [
              dominate
              fake-useragent
              flit
              grequests
              pillow
              readability-lxml
              rich
              typer
              validators
              weasyprint
            ];

            meta = with pkgs.lib; {
              license = licenses.gpl3;
              inherit description homepage maintainers;
            };

            pythonImportsCheck = [ pythonPackage ];

            unpackPhase = ''
              cp -r ${src} .
              sourceRoot=$(ls | grep -v env-vars)
              chmod +w $sourceRoot
              cp ${pyprojectTemplate} $sourceRoot/pyproject.toml
              mkdir $sourceRoot/${pythonPackage}
              cp $sourceRoot/main.py $sourceRoot/${pythonPackage}/${pnameWithUnderscores}.py
            '';

            postInstall = ''
              mkdir $out/bin
              cp -r /build/$sourceRoot/${pythonPackage} $out/lib/python${pythonMajorMinorVersion}/site-packages/
              echo '#!/usr/bin/env sh' > $out/bin/${pnameWithUnderscores}.sh
              echo "export PYTHONPATH=$PYTHONPATH" >> $out/bin/${pnameWithUnderscores}.sh
              echo "${python}/bin/python $out/lib/python${pythonMajorMinorVersion}/site-packages/${pythonPackage}/${pnameWithUnderscores}.py \$@" >> $out/bin/${pnameWithUnderscores}.sh
              chmod +x $out/bin/${pnameWithUnderscores}.sh
            '';

          };
      in rec {
        apps = rec {
          default = dvcoolarun-web2pdf-default;
          dvcoolarun-web2pdf-default = dvcoolarun-web2pdf-python311;
          dvcoolarun-web2pdf-python38 = shared.app-for {
            entrypoint = "${pnameWithUnderscores}.sh";
            package = self.packages.${system}.dvcoolarun-web2pdf-python38;
          };
          dvcoolarun-web2pdf-python39 = shared.app-for {
            entrypoint = "${pnameWithUnderscores}.sh";
            package = self.packages.${system}.dvcoolarun-web2pdf-python39;
          };
          dvcoolarun-web2pdf-python310 = shared.app-for {
            entrypoint = "${pnameWithUnderscores}.sh";
            package = self.packages.${system}.dvcoolarun-web2pdf-python310;
          };
          dvcoolarun-web2pdf-python311 = shared.app-for {
            entrypoint = "${pnameWithUnderscores}.sh";
            package = self.packages.${system}.dvcoolarun-web2pdf-python311;
          };
        };
        defaultPackage = packages.default;
        packages = rec {
          default = dvcoolarun-web2pdf-default;
          dvcoolarun-web2pdf-default = dvcoolarun-web2pdf-python311;
          dvcoolarun-web2pdf-python38 = dvcoolarun-web2pdf-for {
            flit = flit.packages.${system}.flit-python38;
            python = pkgs.python38;
          };
          dvcoolarun-web2pdf-python39 = dvcoolarun-web2pdf-for {
            flit = flit.packages.${system}.flit-python39;
            python = pkgs.python39;
          };
          dvcoolarun-web2pdf-python310 = dvcoolarun-web2pdf-for {
            flit = flit.packages.${system}.flit-python310;
            python = pkgs.python310;
          };
          dvcoolarun-web2pdf-python311 = dvcoolarun-web2pdf-for {
            flit = flit.packages.${system}.flit-python311;
            python = pkgs.python311;
          };
        };
      });
}
