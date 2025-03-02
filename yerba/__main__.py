import argparse
import os
import sys
import threading
import time
from multiprocessing import Process

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .logger_setup import logger
from .main_rutine import MainRutine


def run_main_rutine(filename):
    main_rutine = MainRutine(filename)
    main_rutine.run()


class MarkdownChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, compile_callback):
        super().__init__()
        # Resolve absolute path to avoid mismatches
        self.filename = os.path.abspath(filename)
        self.compile_callback = compile_callback

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.filename:
            self.compile_callback()


def keyboard_listener(compile_callback):
    """
    Unix-based non-blocking keyboard listener.
    Listens for key presses in the background.
    """
    import select
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while True:
            r, _, _ = select.select([sys.stdin], [], [], 0.1)
            if r:
                key = sys.stdin.read(1)
                if key.lower() == "r":
                    compile_callback()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def cli_entry():
    parser = argparse.ArgumentParser(
        description="A CLI application to create markdown-based presentations."
    )

    parser.add_argument("filename", type=str, help="The input filename.")
    parser.add_argument(
        "-l",
        "--listen",
        action="store_true",
        help="Watch the file for changes and recompile automatically.",
    )
    args = parser.parse_args()

    base, ext = os.path.splitext(args.filename)
    filename = args.filename if ext == ".md" else f"{base}.md"

    if not os.path.exists(filename):
        logger.error(f"File '{filename}' not found")
        quit()

    if args.listen:
        logger.info(
            "Listening for changes. [u]Press Ctrl+C to exit[/u].\n",
            extra={"markup": True, "highlighter": None},
        )
        logger.info(
            "Initializing [green]Yerba[/green] "
            "—[i]Built on [green]Manim Community[/green][/i]—",
            extra={"markup": True, "highlighter": None},
        )

        current_process = None

        def start_compilation():
            nonlocal current_process
            # If a compilation is in progress, terminate it.
            if current_process is not None and current_process.is_alive():
                current_process.terminate()
                current_process.join()
            current_process = Process(target=run_main_rutine, args=(filename,))
            current_process.start()

        # Start the initial compilation.
        start_compilation()

        # Start a thread to listen for key press.
        kb_thread = threading.Thread(
            target=keyboard_listener, args=(start_compilation,), daemon=True
        )
        kb_thread.start()

        event_handler = MarkdownChangeHandler(filename, start_compilation)
        observer = Observer()
        # Watch the directory containing the file
        observer.schedule(
            event_handler,
            path=os.path.dirname(os.path.abspath(filename)) or ".",
            recursive=False,
        )
        observer.start()

        # Press Ctrl+C to interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

        # Ensure any running process is terminated when exiting.
        if current_process is not None and current_process.is_alive():
            current_process.terminate()
            current_process.join()
    else:
        logger.info(
            "Initializing [green]Yerba[/green] "
            "—[i]Built on [green]Manim Community[/green][/i]—",
            extra={"markup": True, "highlighter": None},
        )
        run_main_rutine(filename)


if __name__ == "__main__":
    cli_entry()
