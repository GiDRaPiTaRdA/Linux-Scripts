# CheatShell

**CheatShell** is a lightweight, interactive Linux terminal utility for browsing, editing, and running commands saved in a JSON file. Each directory can have its own command collection.

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
      { "Name": "Show current user", "Command": "whoami" },
      { "Name": "Show working directory", "Command": "pwd" },
      { "Name": "Show disk usage", "Command": "df -h" }
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

When you select a command, it appears as an **editable command line**. Edit it if necessary and press **Enter** to run it. The tool exits after the command completes, leaving its output in your terminal. Changes to the command line do not modify the JSON file.

## JSON format

Use `Name` for a visible menu label and either:

- `Children` for a nested list of menu items, or
- `Command` for a Bash command to edit and execute.

Commands run with your user's permissions. **Only use configuration files you trust.**

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
