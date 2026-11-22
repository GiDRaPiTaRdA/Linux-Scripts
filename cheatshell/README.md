# CheatShell

**CheatShell** is an interactive Linux command launcher. Browse nested menus, preview saved commands, edit a command before running it, and keep different commands for different projects.

Requires **Python 3** (with `curses` and `readline`) and **Bash**. No third-party Python packages are required.

## Install

Download only the script:

```bash
tmp=$(mktemp) && \
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py -o "$tmp" && \
sudo install -m 755 "$tmp" /usr/local/bin/cheatshell; rm -f "$tmp"
```

Run `cheatshell`. **On first launch**, it downloads the management menu to `/etc/cheatshell/cheatshell-menu.json` (internet and `sudo` access needed). Run `cheatshell` a second time to open the menu.

## Project commands

CheatShell reads `cheatfile.json` from the **current directory**. Download the [project example](project-cheatfile.json) to try it:

```bash
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/project-cheatfile.json -o cheatfile.json
cheatshell
```

Example `cheatfile.json`:

```json
[
  {
    "Name": "System",
    "Children": [
      {"Name": "Current user", "Command": "whoami"},
      {"Name": "Disk space", "Command": "df -h"}
    ]
  }
]
```

Each entry has a `Name` and either `Children` (submenu) or `Command` (shell command). Optional `Description` text appears in the preview. `Command` accepts a string or an array of strings; array parts are joined with spaces when executed, so include operators such as `&&` where needed. The root JSON may be an array of entries or one named object.

## Optional system commands

Add commands available from every directory using `/etc/cheatshell/system-cheatfile.json`. Download the [system example](system-cheatfile.json) and install it:

```bash
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/system-cheatfile.json -o /tmp/cheatshell-system.json && \
python3 -m json.tool /tmp/cheatshell-system.json >/dev/null && \
sudo install -D -m 644 /tmp/cheatshell-system.json /etc/cheatshell/system-cheatfile.json
```

Menus are shown in this order: **project commands → system commands → CheatShell management**. Project and system commands are optional; the management menu is installed automatically.

## Controls

| Key | Action |
| --- | --- |
| `↑` / `↓` | Navigate |
| `Enter` / `→` | Open submenu or edit selected command |
| `←` / `Esc` | Back / exit |
| `Q` | Quit |

When you select a command, edit the prefilled `$` prompt and press **Enter** to execute. Press **Ctrl+C** to cancel. Changes to the command line aren't saved to JSON. Commands run in a child Bash process, so `cd` and `export` don't change your original shell.

## Check, update, or remove

Inspect loaded configurations:

```bash
cheatshell --check
```

To update, choose **CheatShell → CheatShell management → Update CheatShell** inside the menu, or download and reinstall the latest script using the installation command above.

Uninstall the executable:

```bash
sudo rm /usr/local/bin/cheatshell
```

This leaves your JSON configuration files in place.
