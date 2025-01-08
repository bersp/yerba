__all__ = [
    "ORIGIN", "UP", "DOWN", "RIGHT", "LEFT",
    "IN", "OUT", "UL", "UR", "DL", "DR",
    "PI", "TAU", "DEGREES", "SLIDE_WIDTH", "SLIDE_HEIGHT",
    "SLIDE_X_RAD", "SLIDE_Y_RAD",
    "TOP_EDGE", "BOTTOM_EDGE", "LEFT_EDGE", "RIGHT_EDGE",
    "TL_CORNER", "TR_CORNER", "BL_CORNER", "BR_CORNER",
    "SLIDE_WIDTH_PX", "SLIDE_HEIGHT_PX", "PX"
]

from manim import config
from manim.constants import (
    ORIGIN, UP, DOWN, RIGHT, LEFT, IN, OUT, UL, UR, DL, DR, PI, TAU, DEGREES
)
from manim.typing import Vector3D
import numpy as np


SLIDE_WIDTH: float = config.frame_width
SLIDE_HEIGHT: float = config.frame_height
SLIDE_X_RAD: float = config.frame_x_radius
SLIDE_Y_RAD: float = config.frame_y_radius

TOP_EDGE: Vector3D = np.array((0, SLIDE_Y_RAD, 0))
BOTTOM_EDGE: Vector3D = np.array((0, -SLIDE_Y_RAD, 0))
LEFT_EDGE: Vector3D = np.array((-SLIDE_X_RAD, 0, 0))
RIGHT_EDGE: Vector3D = np.array((SLIDE_X_RAD, 0, 0))

TL_CORNER: Vector3D = np.array((-SLIDE_X_RAD,  SLIDE_Y_RAD, 0))
TR_CORNER: Vector3D = np.array((SLIDE_X_RAD,  SLIDE_Y_RAD, 0))
BL_CORNER: Vector3D = np.array((-SLIDE_X_RAD, -SLIDE_Y_RAD, 0))
BR_CORNER: Vector3D = np.array((SLIDE_X_RAD, -SLIDE_Y_RAD, 0))

SLIDE_WIDTH_PX: float = config.pixel_width
SLIDE_HEIGHT_PX: float = config.pixel_height
PX: float = SLIDE_WIDTH_PX/SLIDE_WIDTH
