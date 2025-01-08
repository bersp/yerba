from __future__ import annotations

from manim_mobject_svg import create_svg_from_vmobject

from manim import VMobject, VGroup, Rectangle

from ..utils.aux_functions import restructure_list_to_exclude_certain_family_members
from .box import Box
from .image import ImageSvg, ImagePDFSvg
from ..utils.aux_classes import LinkedPositionsList
from ..utils.constants import SLIDE_WIDTH, SLIDE_HEIGHT
from ..managers.color_manager import ColorManager


class SubSlide:
    def __init__(
        self,
        slide_number: int,
        subslide_number: int,
        background: VMobject | VGroup | None = None,
    ) -> None:
        """
        Initialize a SubSlide object.

        Parameters
        ----------
        slide_number : int
            The slide number.
        subslide_number : int
            The subslide number.
        background : VMobject, optional
            Custom background (not implemented).
        """

        self.slide_number = slide_number
        self.subslide_number = subslide_number
        self.mobjects = VGroup()

        if background is None:
            background = Rectangle(
                width=SLIDE_WIDTH,
                height=SLIDE_HEIGHT,
                color=ColorManager().get_color("WHITE"),
            )
        if self.subslide_number == 0:
            self.mobjects.add(background.set_z_index(-2))

        self.title: str | None = None
        self.subtitle: str | None = None

    def add(self, mobjects) -> None:
        """Add one or more mobjects to the subslide."""
        self.mobjects.add(*mobjects)

    def remove(self, mobjects) -> None:
        """Remove specified mobjects from the subslide."""
        new_l = restructure_list_to_exclude_certain_family_members(
            self.mobjects, mobjects
        )
        self.mobjects = VGroup(*new_l)

    def write(self) -> None:
        """Write the subslide to an SVG file."""
        out_filename = (
            f"./media/slides/s{self.slide_number:04g}"
            f"_subs{self.subslide_number:04g}.svg"
        )

        vec_mobjects = VGroup()
        img_mobjects = []
        pdf_img_mobjects = []

        for mo in self.mobjects:
            if isinstance(mo, ImageSvg) and mo.draft_mode is False:
                img_mobjects.append(mo)
            elif isinstance(mo, ImagePDFSvg) and mo.draft_mode is False:
                pdf_img_mobjects.append(mo)
            else:
                vec_mobjects += mo

        create_svg_from_vmobject(vec_mobjects, out_filename, crop=False)

        for img in img_mobjects:
            self._write_img(out_filename, img.get_svg_str())

        for pimg in pdf_img_mobjects:
            self._write_img(out_filename, pimg.get_svg_str())

    def _write_img(self, svg_file, svg_str):
        with open(svg_file, "r") as f:
            lines = f.readlines()
        lines.insert(3, svg_str)
        with open(svg_file, "w") as f:
            f.writelines(lines)


class Slide:
    def __init__(self, slide_number: int, background=None) -> None:
        self.slide_number: int = slide_number
        self.subslide_number: int = 0

        self.subslides: list[SubSlide] = [
            SubSlide(slide_number, self.subslide_number, background=background)
        ]

        self.linked_positions = LinkedPositionsList()
        self.boxes: list[Box] = []

    @property
    def mobjects(self):
        return self.subslides[-1].mobjects

    def add_new_subslide(self, n=1, background=None) -> None:
        """
        Generate a new subslide with the same content as the last one.
        """
        if isinstance(n, int):
            for _ in range(n):
                self.subslide_number += 1
                s = SubSlide(
                    self.slide_number, self.subslide_number, background=background
                )
                s.add(self.subslides[-1].mobjects)

                self.subslides.append(s)
        else:
            raise TypeError("'n' must be an int")

    def add_to_subslide(self, mobjects: list, idx=-1) -> list:
        """
        Add mobjects to a subslide.

        Parameters
        ----------
        mobjects : mobject(s)
            One or more mobjects to add.
        idx : int, optional
            Index of the subslide to add to. (Default is -1, which refers to the last subslide)
        """

        to_add = []
        for mo in mobjects:
            box = self._get_box_if_already_exists(mo.box)
            if not box.is_null:
                box.add(mo)
                mo.origin_subslide_number = self.subslide_number
                to_add.append(mo)

        self._add_to_subslide(to_add, idx)

        return mobjects

    def remove_from_subslide(self, mobjects, idx=-1) -> None:
        """
        TODO(bersp): DOC
        """

        return self._remove_from_subslide(mobjects, idx=idx)

    def write(self) -> None:
        """
        Arrange mobjects in their boxes and write the all subslides to SVG files.
        """

        for box in self.boxes:
            box.auto_arrange()

        self.linked_positions.do_aligment()

        for ss in self.subslides:
            ss.write()

    def _add_to_subslide(self, mobjects, idx=-1):
        self.subslides[idx].add(mobjects)

    def _remove_from_subslide(self, mobjects, idx=-1):
        self.subslides[idx].remove(mobjects)

    def _replace_from_last_subslide(self, old_mobject, new_mobject):
        self._remove_from_subslide(old_mobject, idx=-1)
        self._add_to_subslide(new_mobject, idx=-1)

    def _get_box_if_already_exists(self, box):
        """
        Get box if exists in self.boxes, add to it if not.
        """
        if not isinstance(box, Box):
            raise TypeError(f"box must be a Box instance, not {box!r}")
        for b in self.boxes:
            if b == box:
                return b
        else:
            self.boxes.append(box)
            return box
