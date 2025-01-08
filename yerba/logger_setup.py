from manim import logger, console
import logging
from rich.console import Console
from rich.logging import RichHandler

# Silence manim logger
logger.setLevel("ERROR")
logger.handlers[0] = RichHandler(
    console=console,  # this is the manim console
    show_path=False,
    keywords=[],
    log_time_format="%X",
)
del console
del logger

# Console
console = Console()

# Logger
logger = logging.getLogger("yerba")
logger.addHandler(RichHandler(
    console=console,
    show_path=False,
    keywords=[],
    log_time_format="%X",
))
logger.setLevel("INFO")
