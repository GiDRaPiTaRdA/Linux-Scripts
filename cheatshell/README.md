# CheatShell

**CheatShell** is a lightweight Linux terminal menu for browsing and running commands saved in `cheatfile.json`. It supports nested menus, optional descriptions, multiline command previews, and a single editable command prompt before execution.

Requires Python 3 (`curses` and `readline`), Bash, and no third-party Python packages.

## Install

```bash
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py -o cheatshell.py
sudo install -m 755 cheatshell.py /usr/local/bin/cheatshell
```

### Optional shared system commands

```bash
sudo mkdir -p /etc/cheatshell

curl -fL \
  https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/system-cheatfile.json \
  -o /tmp/system-cheatfile.json && \
python3 -m json.tool /tmp/system-cheatfile.json >/dev/null && \
sudo install -m 644 /tmp/system-cheatfile.json /etc/cheatshell/cheatfile.json
```

Rerun the commands to update the shared configuration. Review remote scripts and commands before installing them.

## Configuration

CheatShell loads available files in this order:

1. **Project:** `./cheatfile.json` (current directory)
2. **System:** `/etc/cheatshell/cheatfile.json`

Both are optional, but at least one must exist. Project entries appear first, followed by system entries, with **no automatic nesting**. A root **object** appears as one named menu entry; a root **array** adds its items directly to the menu.

**Named menu:**

```json
{
  "Name": "Minecraft project",
  "Description": "Minecraft server tools",
  "Children": [
    {"Name": "Running containers", "Command": "docker ps"}
  ]
}
```

**Direct menu entries, including a multiline preview:**

```json
[
  {"Name": "Disk space", "Command": "df -h"},
  {
    "Name": "Disk and memory",
    "Description": "Show disk space and RAM usage",
    "Command": ["df -h &&", "free -h"]
  }
]
```

`Name` labels an item, `Description` is optional, `Children` defines a submenu, and `Command` accepts a string or an array of strings. Array elements appear on separate lines **in the preview**, then join with spaces for editing and execution. Include your own Bash operators (`&&`, `;`, `||`, `|`) between commands.

## Run and navigate

Run `cheatshell` from your project directory, or from anywhere if you installed the system cheatfile.

| Key | Action |
| --- | --- |
| `↑` / `↓` | Navigate |
| `Enter` / `→` | Open submenu or edit command |
| `←` / `Esc` | Go back or exit |
| `Q` | Quit |

Selecting a command opens **one prefilled, editable line**. Press **Enter** to run it or **Ctrl+C** to cancel. There is no additional confirmation. Edits do not change the JSON. Commands execute in a child Bash process, so `cd` and `export` do not persist in your original terminal.

## Update or uninstall

Update from GitHub:

```bash
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py -o cheatshell.py && \
python3 -m py_compile cheatshell.py && \
sudo install -m 755 cheatshell.py /usr/local/bin/cheatshell
```

Uninstall the executable (configuration files remain):

```bash
sudo rm /usr/local/bin/cheatshell
```

**Source:** [CheatShell on GitHub](https://github.com/GiDRaPiTaRdA/Linux-Scripts/tree/master/cheatshell)
