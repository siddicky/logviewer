import sys
from os import listdir
from os.path import join

from pylint.lint import Run

THRESHOLD = 9.75

core = [join("core", c) for c in listdir("core") if c.endswith(".py")]

results = Run(["bot.py", *cogs, *core], do_exit=False)

score = results.linter.stats["global_note"]
if score <= THRESHOLD:
    sys.exit(1)
