# CheatShell

**CheatShell** is a lightweight interactive command navigator for Linux. It reads commands from JSON, shows optional descriptions and a multiline preview, then lets you edit the selected command on a single line before running it with Bash.

Keep commands alongside a project, share a common set across the machine, or use both at once. No third-party Python packages are required.

## Features

- Navigate commands and nested menus with arrow keys.
- Preview the selected command; array entries display on separate preview lines.
- Add an optional `Description` to any menu entry.
- Edit the complete command in one prefilled prompt before executing it.
- Use a single command string or an array of command fragments.
- Load **project commands first**, followed by optional **system-wide commands**.
- Use either a root JSON object (kept as a menu item) or a root array (items shown directly).

## Requirements

- Linux terminal with Python 3 and its standard-library `curses` and `readline` modules
- `curl` for the download instructions below
- `sudo` to install system-wide

Commands are executed by `/bin/bash` with the permissions of the current user. Tools referenced by your cheatfile (such as Docker or Git) must be installed separately.

## Install CheatShell

Download the script from the [Linux-Scripts repository](https://github.com/GiDRaPiTaRdA/Linux-Scripts/tree/master/cheatshell):

```bash
curl -fL \
  https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py \
  -o cheatshell.py
```

Review the downloaded script, then install it for all users:

```bash
less cheatshell.py
sudo install -m 755 cheatshell.py /usr/local/bin/cheatshell
command -v cheatshell
```

Expected executable path: `/usr/local/bin/cheatshell`.


## Configuration locations and priority

| Priority | File | Purpose |
| --- | --- | --- |
| 1 | `./cheatfile.json` | Project commands; loaded from the directory where you start CheatShell |
| 2 | `/etc/cheatshell/cheatfile.json` | Shared system commands, available from any directory |

Both are optional, but **at least one must exist**. CheatShell does not currently support a separate user configuration file, and it does not search the parent directories for a project file.

When both exist, their **top-level entries are concatenated in that order**: project first, system second. No extra folder or section is automatically inserted.

If neither exists, CheatShell reports the missing project and system paths. If a present file contains invalid JSON or an unsupported root type, CheatShell reports that file's error rather than silently skipping it.

## Install shared system commands

Create a system-wide config directory and install a trusted JSON configuration:

```bash
sudo mkdir -p /etc/cheatshell
sudo install -m 644 system-cheatfile.json /etc/cheatshell/cheatfile.json
```

The `644` file permissions let all users read the shared commands while restricting writes to the file owner (normally root). Running CheatShell **does not** grant users administrator privileges. Commands containing `sudo` still require their usual authorization.

To change the shared commands later:

```bash
sudoedit /etc/cheatshell/cheatfile.json
```

## Add project commands

Create `cheatfile.json` at the root of your project. For example:

```text
minecraft/
├── cheatfile.json
├── build/
└── server/
```

Run CheatShell from that project directory:

```bash
cd ~/minecraft
cheatshell
```

If a system cheatfile is also installed, its entries appear **after** the project entries.

### Root object: preserve a named menu

A root **object** is kept as one entry. Its `Name` appears on the main menu, and its `Children` are shown only when you open it:

```json
{
  "Name": "Minecraft project",
  "Description": "Build and manage the Minecraft server.",
  "Children": [
    {
      "Name": "Show containers",
      "Description": "List running Docker containers.",
      "Command": "docker ps"
    }
  ]
}
```

### Root array: show items directly

A root **array** contributes each item directly to the main menu, without an extra level:

```json
[
  { "Name": "Git status", "Command": "git status" },
  { "Name": "Disk space", "Command": "df -h" }
]
```

This works for either the project file or the system file. Nested `Children` menus appear exactly where you put them.

## Command format

Each menu item uses:

| Property | Meaning |
| --- | --- |
| `Name` | Display name in the menu |
| `Description` | Optional explanation shown in the preview |
| `Children` | Nested menu entries |
| `Command` | Bash command to edit and execute, either a string or array of strings |

Use `Children` for a submenu, or `Command` for an executable item.

### Single string

```json
{
  "Name": "Memory usage",
  "Description": "Display used and available RAM.",
  "Command": "free -h"
}
```

### Array with multiline preview

```json
{
  "Name": "Disk and memory",
  "Description": "Show disk space and memory usage in sequence.",
  "Command": [
    "df -h &&",
    "free -h"
  ]
}
```

In the menu preview, the two elements appear on **separate lines**:

```text
DESCRIPTION
Show disk space and memory usage in sequence.

COMMAND PREVIEW
df -h &&
free -h
```

When selected, they are joined **with spaces** into a single editable command:

```bash
$ df -h && free -h
```

CheatShell **does not insert separators or backslashes**. Put Bash operators in the JSON yourself:

| Operator | Meaning |
| --- | --- |
| `&&` | Run the next command only if the previous succeeds |
| `;` | Run the next command regardless of success |
| `||` | Run the next command only if the previous fails |
| `|` | Pipe output to another command |

An array is for legibility and preview formatting, **not** separate Bash process execution. All elements become one Bash command string before running.

## Keyboard controls

| Key | Action |
| --- | --- |
| `↑` / `↓` | Select previous / next menu item |
| `Enter` / `→` | Open a submenu or select a command |
| `←` / `Esc` | Back to the parent menu; exit at the top level |
| `Q` | Quit CheatShell |

Highlighting an item updates the optional description and command preview. Longer text wraps; on small terminals, previews may be truncated.

After selecting a command, CheatShell restores the normal terminal and displays **one prefilled command line**. Edit it with the usual terminal editing keys. Press **Enter to execute immediately** or **Ctrl+C to cancel**. There is no additional approval prompt. Editing does not change the JSON file.

The command runs in a separate Bash process. For example, `export VAR=value` and `cd /path` can affect commands within that same Bash invocation, but **cannot change your parent terminal's environment or working directory** after CheatShell exits.

## Update CheatShell from GitHub

To install CheatShell from GitHub:

```bash
curl -fL \
  https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py \
  -o cheatshell.py
python3 -m py_compile cheatshell.py
sudo install -m 755 cheatshell.py /usr/local/bin/cheatshell
```

You can also add this update operation to your **trusted system cheatfile**:

```json
{
  "Name": "Update CheatShell from GitHub",
  "Description": "Download, syntax-check and install CheatShell from the master branch.",
  "Command": [
    "tmp=$(mktemp --suffix=.py) &&",
    "curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py -o \"$tmp\" &&",
    "python3 -m py_compile \"$tmp\" &&",
    "sudo install -m 755 \"$tmp\" /usr/local/bin/cheatshell &&",
    "rm -f \"$tmp\""
  ]
}
```

> This fetches and installs remote code, so review and trust the repository before running it. `py_compile` checks syntax, not safety or runtime correctness. The command installs the script published on the `master` branch.

## Uninstall

```bash
sudo rm /usr/local/bin/cheatshell
```

Shared and project `cheatfile.json` files are not removed automatically. If you also want to delete the system configuration, remove `/etc/cheatshell/cheatfile.json` separately.

## Source

- [CheatShell on GitHub](https://github.com/GiDRaPiTaRdA/Linux-Scripts/tree/master/cheatshell)
