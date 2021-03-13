"""
Some shared scaffolding for building terminal "REPL" drivers.
"""

import curses
from curses.textpad import Textbox, rectangle


def curse_repl(handle_buffer):

    def handle(buff, count):
        try:
            return list(handle_buffer(buff, count)), None
        except Exception as e:
            return None, e

    def _main(stdscr):
        maxy, maxx = 0, 0

        examples = []
        count = 1
        while 1:
            # Prompt
            maxy, maxx = stdscr.getmaxyx()
            stdscr.addstr(0, 0, "Enter example: (hit Ctrl-G to execute, Ctrl-C to exit)", curses.A_BOLD)
            editwin = curses.newwin(5, maxx - 4,
                                    2, 2)
            rectangle(stdscr,
                      1, 1,
                      1 + 5 + 1, maxx - 2)
            stdscr.refresh()

            # Read
            box = Textbox(editwin)
            try:
                box.edit()
            except KeyboardInterrupt:
                break

            # Get resulting contents
            buff = box.gather().strip()
            if not buff:
                continue

            vals, err = handle(buff, count)

            examples.append((count, buff, vals, err))

            # Print
            cur = 8
            def putstr(str, x=0, attr=0):
                nonlocal cur
                # This is how we handle going off the bottom of the scren lol
                if cur < maxy:
                    stdscr.addstr(cur, 0, " " * maxx)  # Shitty line clear
                    stdscr.addstr(cur, x, str, attr)
                    cur += (len(str.split("\n")) or 1)

            for ex, buff, vals, err in reversed(examples):
                putstr(f"Example {ex}", attr=curses.A_BOLD)

                for l in buff.split("\n"):
                    putstr(f"    | {l}")

                putstr("")

                if vals:
                    for x, t in zip(range(1, 1<<64), vals):
                        putstr(f"    {x:<3}) " + repr(t))

                elif err:
                    err = str(err)
                    err = err.split("\n")
                    for l in err:
                        putstr(f"      {l}", attr=curses.COLOR_YELLOW)

                putstr("")

            count += 1
            stdscr.refresh()

    curses.wrapper(_main)
