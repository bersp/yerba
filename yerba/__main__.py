import sys
import os

from .logger_setup import logger
from .main_rutine import MainRutine


def cli_entry():
    if len(sys.argv) == 1:
        logger.info("You should specify an input filename")
        quit()
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
        if os.path.exists(filename):
            pass
        elif os.path.exists(filename+".md"):
            filename = filename+".md"
        else:
            logger.error(f"File '{filename}' not found")
            quit()
    else:
        logger.error("Too many args")
        quit()

    main_rutine = MainRutine(filename)
    main_rutine.run()


if __name__ == "__main__":
    cli_entry()
