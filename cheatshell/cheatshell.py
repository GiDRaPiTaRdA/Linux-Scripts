#!/usr/bin/env python3

import curses
import json
import readline
import subprocess
import sys
import textwrap
from pathlib import Path

PROJECT_CONFIG = Path.cwd() / "cheatfile.json"
SYSTEM_CONFIG = Path("/etc/cheatshell/cheatfile.json")


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
        result = subprocess.run(
            edited, shell=True, executable="/bin/bash", check=False
        )
        return result.returncode
    except KeyboardInterrupt:
        return 130


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


def load_commands():
    # Project entries appear first, followed by optional system entries.
    # Named root objects retain their own submenu; arrays remain flat.
    paths = (PROJECT_CONFIG, SYSTEM_CONFIG)
    found = [path for path in paths if path.is_file()]
    if not found:
        print("No CheatShell configuration found:")
        print(f"  Project config not found: {PROJECT_CONFIG}")
        print(f"  System config not found:  {SYSTEM_CONFIG}")
        sys.exit(1)

    commands = []
    for path in found:
        try:
            commands.extend(load_config(path))
        except (json.JSONDecodeError, OSError, ValueError) as error:
            print(f"Error loading config {path}: {error}")
            sys.exit(1)
    return commands

if __name__ == "__main__":
    commands = load_commands()
    try:
        selected_command = curses.wrapper(main, commands)
    except KeyboardInterrupt:
        print()
        sys.exit(130)

    if selected_command is not None:
        sys.exit(edit_and_execute(selected_command))
