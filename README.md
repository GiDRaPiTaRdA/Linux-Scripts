# Linux Scripts

A collection of lightweight Linux scripts and command-line utilities.

## Tools

| Tool | Description |
| --- | --- |
| [CheatShell](cheatshell/README.md) | Browse, edit, and run saved shell commands from interactive menus. |

## Install CheatShell

Download only the Python script — no repository clone required:

```bash
tmp=$(mktemp) && \
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py -o "$tmp" && \
sudo install -m 755 "$tmp" /usr/local/bin/cheatshell; rm -f "$tmp"
```

Run `cheatshell`. On first launch, it downloads and installs its management menu (requires internet access and permission to use `sudo`). Run `cheatshell` again to open the menu.

See the [CheatShell README](cheatshell/README.md) for configuration, usage, and updating.
