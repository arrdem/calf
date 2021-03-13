"""
Some shared scaffolding for building terminal "REPL" drivers.
"""

import curses
from curses.textpad import Textbox, rectangle


def curse_repl(handle_buffer):

    def _main(stdscr):
        maxy, maxx = stdscr.getmaxyx()

        examples = []
        count = 1
        while 1:
            # Prompt
            stdscr.addstr(0, 0, "Enter example: (hit Ctrl-G to execute, Ctrl-C to exit)", curses.A_BOLD)
            editwin = curses.newwin(5, maxx - 4,
                                    2, 2)
            rectangle(stdscr,
                      1, 1,
                      1 + 5 + 1, maxx - 2)
            stdscr.refresh()

            # Read
            box = Textbox(editwin)
            box.edit()

            # Get resulting contents
            buff = box.gather().strip()
            assert buff

            examples.append((count, buff, list(handle_buffer(buff, count))))

            # Print
            cur = 8
            def putstr(str, x=0, attr=0):
                nonlocal cur
                # This is how we handle going off the bottom of the scren lol
                if cur < maxy:
                    stdscr.addstr(cur, x, str, attr)
                    cur += (len(str.split("\n")) or 1)

            for ex, buff, tokens in reversed(examples):
                putstr(f"Example {ex}", attr=curses.A_BOLD)

                for l in buff.split("\n"):
                    putstr(f"    | {l}")

                putstr("")

                for x, t in zip(range(1, 1<<64), tokens):
                    putstr(f"    {x:<3}) " + repr(t))

                putstr("")

            count += 1
            stdscr.refresh()

    curses.wrapper(_main)
