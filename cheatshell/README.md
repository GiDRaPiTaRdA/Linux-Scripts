# CheatShell

**CheatShell** is a lightweight, interactive Linux terminal utility for browsing, previewing, editing, and running commands saved in a JSON file. Each directory can have its own command collection.

You can still type shell commands normally; CheatShell is a convenient way to recall longer commands when you want them.

## Requirements

- Linux terminal with Python 3, including the standard-library `curses` and `readline` modules
- `curl` for the direct-download installation method
- `sudo` for the system-wide installation method

No third-party Python packages are required.

## Install (only the script)

Download the Python script directly from GitHub; you **do not** need to clone the repository:

```bash
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py -o cheatshell.py
```

Optionally inspect the file before installing it:

```bash
less cheatshell.py
```

Install the command globally:

```bash
sudo install -m 755 cheatshell.py /usr/local/bin/cheatshell
```

Check that it is available:

```bash
command -v cheatshell
```

Expected path: `/usr/local/bin/cheatshell`.

> This download URL assumes `cheatshell/cheatshell.py` is published on the `master` branch of [GiDRaPiTaRdA/Linux-Scripts](https://github.com/GiDRaPiTaRdA/Linux-Scripts).

## Create your command file

CheatShell looks for **`cheatfile.json` in the directory where you launch it**. It does not search parent folders.

You can download the sample configuration separately:

```bash
mkdir -p ~/cheatshell-test
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatfile.example.json -o ~/cheatshell-test/cheatfile.json
cd ~/cheatshell-test
cheatshell
```

Alternatively, create `cheatfile.json` manually:

```json
[
  {
    "Name": "System",
    "Children": [
      { "Name": "Show current user", "Description": "Print the current Linux username.", "Command": "whoami" },
      { "Name": "Show working directory", "Command": "pwd" },
      { "Name": "Show disk usage", "Description": "Display free and used disk space.", "Command": "df -h" },
      {
        "Name": "Disk and memory",
        "Description": "Show disk space and memory usage sequentially.",
        "Command": [
          "df -h &&",
          "free -h"
        ]
      }
    ]
  },
  {
    "Name": "Testing",
    "Children": [
      { "Name": "Hello world", "Command": "echo 'Hello from CheatShell!'" },
      { "Name": "Show date", "Command": "date" }
    ]
  }
]
```

## Run

Go to a folder that contains `cheatfile.json`, then run:

```bash
cd ~/cheatshell-test
cheatshell
```

Your menus come from that folder's JSON configuration, not from the installation directory. If the file is missing, CheatShell reports that no commands file was found.

## Keyboard controls

| Key | Action |
| --- | --- |
| Up / Down | Move through menu items |
| Enter / Right | Open a submenu or select a command |
| Left / Esc | Return to the parent menu or exit |
| Q | Exit the navigator |

When you highlight an entry, the menu shows its **optional description** and a **command preview**. For a `Command` array, each element is displayed on its own line; long entries wrap to fit the terminal. Previews may be truncated in smaller terminals.

Selecting a command opens the **original single-line editable prompt**. CheatShell combines array elements with spaces, pre-fills the resulting command, and lets you review or edit it. Press **Enter** to execute the edited command, or **Ctrl+C** to cancel. There is no separate approval screen: pressing Enter at this prompt runs the command.

The tool exits after the command completes, leaving its output in your terminal. Changes made in the prompt do **not** modify `cheatfile.json`.

## JSON format

Use these fields in each menu entry:

- `Name` — label displayed in the menu.
- `Description` *(optional)* — explanatory text shown below the highlighted item.
- `Children` — nested menu entries, **or** `Command` — a command to edit and run.

`Command` accepts **either a string** (the original format) **or an array of strings** (for visually organizing longer command sequences in JSON). Both formats are supported in the same file.

### Single-line command

```json
{
  "Name": "Disk space",
  "Description": "Show disk usage in human-readable units.",
  "Command": "df -h"
}
```

### Multiline preview with a `Command` array

```json
{
  "Name": "Disk and memory",
  "Description": "Display disk space, then memory usage.",
  "Command": [
    "df -h &&",
    "free -h"
  ]
}
```

The preview shows the array as separate lines:

```text
COMMAND PREVIEW
 df -h &&
 free -h
```

When selected, it becomes **one editable line**:

```bash
$ df -h && free -h
```

CheatShell joins array elements **with spaces only**. It does **not** insert separators or newlines when executing. Include Bash operators explicitly between independent commands:

| Operator | Behavior |
| --- | --- |
| `&&` | Run the next command only if the previous succeeds |
| `;` | Run the next command regardless of success |
| `||` | Run the next command only if the previous fails |
| `|` | Pipe output into the next command |

For example, use `"df -h &&"` before `"free -h"`, **not** two separate commands without an operator; joining them without an operator would create a different shell command.

Commands execute using Bash with your user's permissions. Any environment variables set inside a selected command are local to its subprocess and do not persist in the terminal that launched CheatShell. **Only use configuration files you trust.**

## Update

Download the latest published script and replace the installed copy:

```bash
curl -fL https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/cheatshell.py -o cheatshell.py
sudo install -m 755 cheatshell.py /usr/local/bin/cheatshell
```

## Uninstall

```bash
sudo rm /usr/local/bin/cheatshell
```

Uninstalling the executable does not delete your own `cheatfile.json` files.

## Source code

[CheatShell on GitHub](https://github.com/GiDRaPiTaRdA/Linux-Scripts/tree/master/cheatshell)
