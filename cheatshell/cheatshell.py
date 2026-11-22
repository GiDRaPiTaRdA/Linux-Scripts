#!/usr/bin/env python3

import curses
import os
import tempfile
import urllib.error
import urllib.request
import json
import readline
import subprocess
import sys
import textwrap
from pathlib import Path

PROJECT_CONFIG = Path.cwd() / "cheatfile.json"
SYSTEM_CONFIG = Path("/etc/cheatshell/system-cheatfile.json")
MENU_CONFIG = Path("/etc/cheatshell/cheatshell-menu.json")
GITHUB_RAW = "https://raw.githubusercontent.com/GiDRaPiTaRdA/Linux-Scripts/master/cheatshell/"

# Management commands are maintained exclusively in cheatshell-menu.json.
# On first launch, CheatShell downloads this file from the project repository.


def preview_lines(item, width):
    """Format the highlighted item's optional description and command preview."""
    lines = []
    description = item.get("Description")
    if isinstance(description, str) and description.strip():
        lines.append("DESCRIPTION")
        lines.extend(textwrap.wrap(description.strip(), width=width) or [""])
        lines.append("")

    command = item.get("Command")
    if command is not None:
        lines.append("COMMAND PREVIEW")
        if isinstance(command, str):
            parts = [command]
        elif isinstance(command, list):
            parts = command
        else:
            parts = ["[Invalid Command value]"]
        for part in parts:
            if not isinstance(part, str):
                part = "[Invalid command element]"
            # Keep each array item on its own preview line, wrapping only
            # when necessary to fit the terminal width.
            lines.extend(textwrap.wrap(part, width=width, replace_whitespace=False,
                                       drop_whitespace=False, break_long_words=True,
                                       break_on_hyphens=False) or [""])
    return lines


def draw_menu(stdscr, title, items, selected):
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    def write(y, text, style=0):
        if 0 <= y < height and width > 4:
            try:
                stdscr.addnstr(y, 2, text, width - 4, style)
            except curses.error:
                pass

    write(0, "COMMAND CHEAT MENU", curses.A_BOLD)
    write(1, title)
    write(2, "─" * max(0, width - 4))

    # Reserve the lower part of the screen for a multiline preview while
    # leaving enough space for navigating the command list.
    item = items[selected]
    preview = preview_lines(item, max(1, width - 4))
    if preview and height >= 11:
        preview_height = min(max(4, height // 3), height - 7)
        menu_height = height - preview_height - 6
    else:
        preview_height = 0
        menu_height = max(1, height - 5)

    visible_rows = max(1, menu_height)
    offset = max(0, selected - visible_rows + 1)
    for row, i in enumerate(range(offset, min(len(items), offset + visible_rows))):
        entry = items[i]
        name = entry.get("Name", "Unnamed")
        prefix = "[+] " if "Children" in entry else "    "
        marker = ">" if i == selected else " "
        style = (
            curses.color_pair(1)
            if i == selected and curses.has_colors()
            else curses.A_REVERSE if i == selected else curses.A_NORMAL
        )
        write(row + 3, f"{marker} {prefix}{name}", style)

    if preview_height:
        separator_y = height - preview_height - 3
        write(separator_y, "─" * max(0, width - 4))
        # If content exceeds the available preview area, show its start and
        # mark truncation explicitly rather than spilling into the footer.
        available = preview_height
        shown = preview[:available]
        if len(preview) > available:
            shown[-1] = "... (preview truncated; Enter to edit full command)"
        for row, line in enumerate(shown):
            style = curses.A_BOLD if line in ("DESCRIPTION", "COMMAND PREVIEW") else 0
            write(separator_y + 1 + row, line, style)

    write(height - 2, "↑/↓ Navigate | Enter Select/Edit & Run | ← Back | Q Exit")
    stdscr.refresh()


def main(stdscr, root):
    curses.curs_set(0)
    stdscr.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        if curses.COLORS >= 256:
            curses.init_pair(1, 16, 32)
        else:
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)

    stack = [("Home", root, 0)]
    while stack:
        title, items, selected = stack[-1]
        if not items:
            if len(stack) > 1:
                stack.pop()
                continue
            return None

        draw_menu(stdscr, title, items, selected)
        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(items)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(items)
        elif key in (10, 13, curses.KEY_ENTER, curses.KEY_RIGHT):
            item = items[selected]
            if "Children" in item:
                stack[-1] = (title, items, selected)
                stack.append((title + " / " + item["Name"], item["Children"], 0))
                continue
            if "Command" in item:
                # Return selected command; curses.wrapper restores terminal first.
                return item["Command"]
        elif key in (curses.KEY_LEFT, 27):
            if len(stack) > 1:
                stack.pop()
                continue
            return None
        elif key in (ord("q"), ord("Q")):
            return None
        stack[-1] = (title, items, selected)


def edit_and_execute(command):
    # The cheatfile may supply one command as a string or several pieces as
    # an array. Join them with spaces so operators (&&, ;, ||) remain explicit
    # in the cheatfile, and keep the original single-line edit/execute flow.
    if isinstance(command, list):
        if not all(isinstance(part, str) for part in command):
            print("Error: Every Command array element must be a string.")
            return 1
        command = " ".join(part.strip() for part in command)
    elif not isinstance(command, str):
        print("Error: Command must be a string or an array of strings.")
        return 1

    # This runs after curses.wrapper has restored the normal terminal.
    readline.set_startup_hook(lambda: readline.insert_text(command))
    try:
        try:
            edited = input("$ ")
        except (KeyboardInterrupt, EOFError):
            print()
            return 130
    finally:
        readline.set_startup_hook(None)

    if not edited.strip():
        return 0
    try:
        # Let Bash write stdout and stderr directly to the terminal. This
        # preserves interactive programs (sudo, nano, read prompts, etc.) and
        # lets users see the actual error message instead of an exit code.
        result = subprocess.run(
            edited, shell=True, executable="/bin/bash", check=False
        )
    except KeyboardInterrupt:
        print("\nCommand interrupted.")
        return 130
    except OSError as error:
        print(f"\nCommand could not start: {error}", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print("\n✗ Command failed. Check the error message above.", file=sys.stderr)
    return result.returncode


def load_config(path):
    """Read top-level menu entries without changing the JSON hierarchy.

    A JSON array contributes its items directly to the main menu.
    A JSON object is kept as one item, including its Name and Children.
    """
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    if isinstance(data, list):
        commands = data
    elif isinstance(data, dict):
        commands = [data]
    else:
        raise ValueError("root must be a JSON array or object")
    if not all(isinstance(item, dict) for item in commands):
        raise ValueError("each top-level command must be a JSON object")
    return commands


def validate_menu(path):
    """Verify the downloaded management menu before installing it."""
    menu = load_config(path)
    if (len(menu) != 1 or menu[0].get("Name") != "CheatShell"
            or not isinstance(menu[0].get("Children"), list)):
        raise ValueError('management menu must be one "CheatShell" object with Children')
    return menu


def ensure_menu_installed():
    """Install the GitHub management menu on first launch, then read it from disk."""
    if MENU_CONFIG.is_file():
        return
    if MENU_CONFIG.exists():
        raise RuntimeError(f"Not a regular file: {MENU_CONFIG}")

    print(f"Management menu missing: {MENU_CONFIG}", flush=True)
    print("Downloading cheatshell-menu.json from GitHub...", flush=True)
    temp_path = None
    try:
        temp_path = download_to_temp("cheatshell-menu.json")
        validate_menu(temp_path)
        # GNU install supports -D (create parent directory), but NOT -n.
        # Do not elevate the whole application: only the installation step.
        if os.geteuid() == 0:
            install_cmd = ["install", "-D", "-m", "644", str(temp_path), str(MENU_CONFIG)]
        else:
            install_cmd = ["sudo", "install", "-D", "-m", "644", str(temp_path), str(MENU_CONFIG)]
        subprocess.run(install_cmd, check=True)
        print(f"Installed {MENU_CONFIG}", flush=True)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    if not MENU_CONFIG.is_file():
        raise RuntimeError(f"Installation did not produce {MENU_CONFIG}")


def load_commands():
    """Project first, then system, then the mandatory CheatShell menu."""
    commands = []
    for path in (PROJECT_CONFIG, SYSTEM_CONFIG):
        if not path.is_file():
            continue
        try:
            commands.extend(load_config(path))
        except (json.JSONDecodeError, OSError, ValueError) as error:
            print(f"Error loading config {path}: {error}")
            sys.exit(1)

    # The required management menu is loaded from disk, never from Python.
    try:
        commands.extend(validate_menu(MENU_CONFIG))
    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Error loading CheatShell menu {MENU_CONFIG}: {error}", file=sys.stderr)
        sys.exit(1)
    return commands


def download_to_temp(filename):
    """Download a repository file to a temporary, privately owned file."""
    url = GITHUB_RAW + filename
    with urllib.request.urlopen(url, timeout=25) as response:
        content = response.read(2_000_001)
    if len(content) > 2_000_000:
        raise ValueError("Downloaded file is unexpectedly large")
    with tempfile.NamedTemporaryFile(mode="wb", delete=False, prefix="cheatshell-") as tmp:
        tmp.write(content)
        return Path(tmp.name)


if __name__ == "__main__":
    first_run = not MENU_CONFIG.exists()
    try:
        ensure_menu_installed()
    except (OSError, ValueError, RuntimeError, urllib.error.URLError, subprocess.CalledProcessError) as error:
        print(f"Could not initialize CheatShell management menu: {error}", file=sys.stderr)
        print("Install /etc/cheatshell/cheatshell-menu.json manually or check network and sudo access.", file=sys.stderr)
        sys.exit(1)

    if first_run:
        print("CheatShell management menu installed successfully.")
        print("Run 'cheatshell' again to open the menu.")
        sys.exit(0)

    commands = load_commands()
    if "--check" in sys.argv[1:]:
        print(f"Executable: {Path(__file__).resolve()}")
        print(f"Project: {PROJECT_CONFIG} ({'found' if PROJECT_CONFIG.is_file() else 'missing'})")
        print(f"System: {SYSTEM_CONFIG} ({'found' if SYSTEM_CONFIG.is_file() else 'missing'})")
        print(f"Management: {MENU_CONFIG} ({'found' if MENU_CONFIG.is_file() else 'missing'})")
        print(f"Loaded {len(commands)} top-level menu entries:")
        for index, item in enumerate(commands, start=1):
            print(f"  {index}. {item.get('Name', '(unnamed)')}")
        sys.exit(0)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        print("CheatShell needs an interactive terminal (TTY).", file=sys.stderr)
        sys.exit(1)
    if not commands:
        print("CheatShell found no menu entries.", file=sys.stderr)
        sys.exit(1)
    try:
        selected = curses.wrapper(main, commands)
    except KeyboardInterrupt:
        print()
        sys.exit(130)

    if selected is not None:
        sys.exit(edit_and_execute(selected))
