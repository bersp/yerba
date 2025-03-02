import argparse
import os

from .logger_setup import logger
from .main_rutine import MainRutine


def cli_entry():
    parser = argparse.ArgumentParser(
        description="A CLI application to create markdown base presentations."
    )

    parser.add_argument("filename", type=str, help="The input filename.")

    args = parser.parse_args()

    base, ext = os.path.splitext(args.filename)
    filename = args.filename if ext == ".md" else f"{base}.md"

    if not os.path.exists(filename):
        logger.error(f"File '{filename}' not found")
        quit()

    main_rutine = MainRutine(filename)
    main_rutine.run()


if __name__ == "__main__":
    cli_entry()
