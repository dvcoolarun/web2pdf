# dvcoolarun/web2pdf nix flake

[Nix](https://nixos.org "Nix") flake for <https://github.com/dvcoolarun/web2pdf>.

## Usage

``` sh
nix run github:dvcoolarun/web2pdf?dir=nix
```

The default is python 3.11. However, there are other Python versions available:

- Python 3.8: `nix run github:dvcoolarun/web2pdf?dir=nix#dvcoolarun-web2pdf-python38`
- Python 3.9: `nix run github:dvcoolarun/web2pdf?dir=nix#dvcoolarun-web2pdf-python39`
- Python 3.10: `nix run github:dvcoolarun/web2pdf?dir=nix#dvcoolarun-web2pdf-python310`
- Python 3.11: `nix run github:dvcoolarun/web2pdf?dir=nix#dvcoolarun-web2pdf-python311`

## How to declare it in your flake

Check the latest tag of the definition repository: <https://github.com/dvcoolarun/web2pdf/tags>, and use it instead of the `[version]` placeholder below.

```nix
{
  description = "[..]";
  inputs = rec {
    [..]
    dvcoolarun-web2pdf = {
      [optional follows]
      url =
        "github:dvcoolarun/web2pdf/[version]?dir=nix";
    };
  };
  outputs = [..]
};
```

If your project depends upon [https://github.com/nixos/nixpkgs](nixpkgs "nixpkgs") and/or [https://github.com/numtide/flake-utils](flake-utils "flake-utils"), you might want to pin them under the `[optional follows]` above.

Use the specific package depending on your system (one of `flake-utils.lib.defaultSystems`) and Python version:

- `#packages.[system].dvcoolarun-web2pdf-python38` 
- `#packages.[system].dvcoolarun-web2pdf-python39` 
- `#packages.[system].dvcoolarun-web2pdf-python310` 
- `#packages.[system].dvcoolarun-web2pdf-python311`
