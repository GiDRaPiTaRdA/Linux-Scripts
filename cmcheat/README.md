# CmCheat

**CmCheat** is a lightweight, interactive command launcher for Linux. Keep reusable commands in a `nav_commands.json` file in each project directory, browse them using your keyboard, edit a command before running it, and execute it from the terminal.

CmCheat does **not** replace your shell. You can keep typing commands normally; it simply makes longer or frequently used commands easier to recall.

## Features

- Loads `nav_commands.json` from **the current working directory only**.
- Supports nested command categories.
- Uses arrow keys to navigate.
- Lets you edit a selected command before execution.
- Runs commands through Bash, displaying their normal terminal output.
- Exits after the command finishes.
- Uses Python's standard library; no third-party Python packages required.

## Requirements

- Linux terminal (including WSL and SSH sessions)
- Python 3 with `curses` and `readline` support
- Bash (`/bin/bash`)

Check Python with:

```bash
python3 --version
python3 -c 'import curses, readline; print("Ready")'
```

## Install

Clone or download this repository, then run the following **from the repository folder**:

```bash
sudo install -m 755 cmcheat.py /usr/local/bin/cmcheat
```

> **Note:** If your script is currently named `menu.py`, rename the repository copy to `cmcheat.py` first: `mv menu.py cmcheat.py`. The first line of the Python file must be `#!/usr/bin/env python3`.

Verify the installation:

```bash
command -v cmcheat
```

Expected path: `/usr/local/bin/cmcheat`.

To update after editing or pulling a new version, run the same `sudo install` command again.

## Quick start

Create a folder for testing and copy the example configuration into it:

```bash
mkdir -p ~/cmcheat-demo
cp nav_commands.example.json ~/cmcheat-demo/nav_commands.json
cd ~/cmcheat-demo
cmcheat
```

The `cp` command above assumes you're in the repository directory; otherwise, specify the full path to `nav_commands.example.json`.

Select **Testing → Hello world**, edit the proposed command if you like, then press Enter to execute it.

### Keyboard controls

| Key | Action |
| --- | --- |
| Up / Down | Move through items |
| Enter / Right arrow | Open a category or edit a command |
| Left arrow / Esc | Go back; exit at the top level |
| Q | Exit CmCheat |

When editing a command, press **Enter** to execute it or **Ctrl+C** to cancel. The original JSON entry is not modified.

## Configuration

CmCheat looks for a file named **`nav_commands.json` in the directory where you run `cmcheat`**. It does not automatically search parent directories.

Example:

```text
~/projects/my-app/
├── nav_commands.json
└── ...
```

```bash
cd ~/projects/my-app
cmcheat
```

If the file is absent, CmCheat prints `No commands file found: ...` and exits.

### JSON format

The top-level value is an array. Each entry has a `Name` and either `Children` (a submenu) or `Command` (a Bash command):

```json
[
  {
    "Name": "System",
    "Children": [
      { "Name": "Who am I?", "Command": "whoami" },
      { "Name": "Current directory", "Command": "pwd" }
    ]
  },
  { "Name": "List files", "Command": "ls -lah" }
]
```

- `Name`: Display label.
- `Children`: Array of nested menu items.
- `Command`: Shell command to propose for editing and execution.

Commands run using Bash and inherit the directory from which you launched CmCheat. For example, you can store a Docker Compose command in the appropriate project's configuration file.

Because JSON uses double quotes, any double quotes *inside* a command string must be escaped as `\"`.

Validate a configuration:

```bash
python3 -m json.tool nav_commands.json > /dev/null && echo 'JSON valid'
```

## Project layout

```text
cmcheat/
├── cmcheat.py
├── nav_commands.example.json
└── README.md
```

For personal projects, keep `nav_commands.json` in the project itself rather than alongside the globally installed program.

## Uninstall

```bash
sudo rm /usr/local/bin/cmcheat
```

This removes the executable, not your project configuration files.

## Security

**Only use configuration files you trust.** CmCheat runs commands from JSON with your account's permissions. Review commands before executing them, especially when using configuration files downloaded from other people. Avoid storing passwords or API tokens in command strings.
