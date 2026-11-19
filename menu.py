#!/usr/bin/env python3

import curses
import json
import readline
import subprocess
import sys
from pathlib import Path

CONFIG = Path.cwd() / "nav_commands.json"


def draw_menu(stdscr, title, items, selected):
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    def write(y, text, style=0):
        if 0 <= y < height and width > 4:
            try:
                stdscr.addnstr(y, 2, text, width - 4, style)
            except curses.error:
                pass

    write(0, "COMMAND NAVIGATOR", curses.A_BOLD)
    write(1, title)
    write(2, "─" * max(0, width - 4))

    # Keep the selected option visible
    visible_rows = max(1, height - 7)
    offset = max(0, selected - visible_rows + 1)

    for row, i in enumerate(
        range(offset, min(len(items), offset + visible_rows))
    ):
        item = items[i]
        name = item.get("Name", "Unnamed")

        prefix = "[+] " if "Children" in item else "    "
        marker = ">" if i == selected else " "

        # Blue background with black text
        style = (
            curses.color_pair(1)
            if i == selected
            else curses.A_NORMAL
        )

        write(row + 3, f"{marker} {prefix}{name}", style)

    write(
        height - 2,
        "↑/↓ Navigate | Enter Select | ← Back | Q Exit"
    )

    stdscr.refresh()


def edit_and_execute(stdscr, command):
    # Return terminal to normal mode
    curses.endwin()

    # Clear below cursor without clearing terminal history
    print("\033[0J", end="", flush=True)

    # Prefill editable command
    readline.set_startup_hook(
        lambda: readline.insert_text(command)
    )

    try:
        edited = input("$ ")

    except (KeyboardInterrupt, EOFError):
        print()
        return

    finally:
        readline.set_startup_hook(None)

    if not edited.strip():
        return

    try:
        # Run command through Bash without echoing it again
        result = subprocess.run(
            edited,
            shell=True,
            executable="/bin/bash",
            check=False,
        )
        sys.exit(result.returncode)

    except KeyboardInterrupt:
        sys.exit(130)


def main(stdscr, root):
    curses.curs_set(0)
    stdscr.keypad(True)

    # 256-color palette:
    # Foreground 16 = black
    # Background 74 = light blue
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()

        if curses.COLORS >= 256:
            curses.init_pair(1, 16, 32)
        else:
            curses.init_pair(
                1,
                curses.COLOR_BLACK,
                curses.COLOR_BLUE
            )

    stack = [("Home", root, 0)]

    while stack:
        title, items, selected = stack[-1]

        if not items:
            if len(stack) > 1:
                stack.pop()
                continue
            break

        draw_menu(stdscr, title, items, selected)
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(items)

        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(items)

        elif key in (
            10,
            13,
            curses.KEY_ENTER,
            curses.KEY_RIGHT
        ):
            item = items[selected]

            if "Children" in item:
                stack[-1] = (title, items, selected)

                stack.append((
                    title + " / " + item["Name"],
                    item["Children"],
                    0
                ))
                continue

            elif "Command" in item:
                edit_and_execute(stdscr, item["Command"])
                return

        elif key in (curses.KEY_LEFT, 27):
            if len(stack) > 1:
                stack.pop()
                continue
            break

        elif key in (ord("q"), ord("Q")):
            break

        stack[-1] = (title, items, selected)


def load_commands():
    if not CONFIG.is_file():
        print(f"No commands file found: {CONFIG}")
        sys.exit(1)

    try:
        with CONFIG.open(encoding="utf-8") as file:
            commands = json.load(file)

        if not isinstance(commands, list):
            raise ValueError(
                "nav_commands.json must contain a JSON array."
            )

        return commands

    except (json.JSONDecodeError, OSError, ValueError) as error:
        print(f"Error loading commands: {error}")
        sys.exit(1)


if __name__ == "__main__":
    commands = load_commands()

    try:
        curses.wrapper(main, commands)
    except KeyboardInterrupt:
        print()
