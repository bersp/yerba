from __future__ import annotations
from typing import NamedTuple
from manim import VMobject, VGroup, UP, LEFT, RIGHT, ORIGIN

from ..base.box import Box

class LinkedPositions(NamedTuple):
    source: VMobject | list[VMobject]
    destination: VMobject | VGroup
    align: str | Box | None


class LinkedPositionsList(list[LinkedPositions]):
    def do_aligment(self):
        for lmp in self:
            if isinstance(lmp.source, list):
                src_list = lmp.source
            else:
                src_list = [lmp.source]
            dst = lmp.destination

            if lmp.align == "dest":
                align = dst[0].box.arrange  # type: ignore
            elif isinstance(lmp.align, Box):
                align = lmp.align.arrange
            else:
                align = lmp.align

            assert isinstance(align, str) or align is None, (
                f"'arrange' must be a str, not {repr(align)}")

            if align == "hcenter":
                VGroup(*src_list).align_to(dst, UP)
            elif align == "center" or align is None:
                VGroup(*src_list).move_to(dst)
            else:
                d = align.split(" ")
                if len(d) != 2:
                    raise ValueError(f"{repr(align)} is not a valid alignment")
                else:
                    d1, d2 = d
                alignment = ORIGIN.copy()
                if d1 == "top":
                    alignment += UP
                if d2 == "left":
                    alignment += LEFT
                elif d2 == "right":
                    alignment += RIGHT
                VGroup(*src_list).align_to(dst, alignment)
