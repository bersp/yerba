from __future__ import annotations

import operator
from functools import reduce

from manim import SVGMobject, Tex, Text, TexTemplate
from manim.constants import SCALE_FACTOR_PER_FONT_POINT
from manim.utils.tex_file_writing import tex_to_svg_file

from ..managers.color_manager import ColorManager
from ..utils.aux_functions import define_default_kwargs
from ..utils.latex import process_enhanced_text
from .properties import funcs_from_props


class Ytex(Tex):
    def __init__(
        self, text, style="regular", subslide_number: int | None = None, **tex_kwargs
    ):
        tex_kwargs = define_default_kwargs(tex_kwargs, font_size=30, color="BLACK")
        tex_kwargs["color"] = ColorManager().get_color(tex_kwargs["color"])
        text, ismo_props_zip = process_enhanced_text(text)

        if style == "regular":
            super().__init__(text, **tex_kwargs)
        elif style == "bold_italic":
            super().__init__(rf"\textbf{{\textit{{{text}}}}}", **tex_kwargs)
        else:
            try:
                style = {"bold": "textbf", "italic": "textit"}[style]
            except KeyError:
                raise ValueError(
                    "'style' must be 'regular', 'bold', 'italic' or 'bold_italic'"
                )
            super().__init__(rf"\{style}{{{text}}}", **tex_kwargs)

        for imo, props in ismo_props_zip:
            mo = self if imo == -1 else self.submobjects[imo]

            if "id" in props and subslide_number is not None:
                mo.origin_subslide_number = subslide_number  # type: ignore

            funcs, _ = funcs_from_props(props)
            for f in funcs:
                f(mo)


class Ycode(SVGMobject):
    """
    Copy of Manim.text_mobject.SingleStringMathTex with minnor modifications.
    """

    def __init__(
        self,
        tex_string: str,
        tex_template: TexTemplate,
        stroke_width: float = 0,
        should_center: bool = True,
        height: float | None = None,
        organize_left_to_right: bool = False,
        tex_environment: str = "align*",
        font_size: float = 30,
        **kwargs,
    ):
        self._font_size = font_size
        self.organize_left_to_right = organize_left_to_right
        self.tex_environment = tex_environment
        self.tex_template = tex_template

        assert isinstance(tex_string, str)
        self.tex_string = tex_string
        file_name = tex_to_svg_file(
            self._get_modified_expression(tex_string),
            environment=self.tex_environment,
            tex_template=self.tex_template,
        )
        super().__init__(
            file_name=file_name,
            should_center=should_center,
            stroke_width=stroke_width,
            height=height,
            path_string_config={
                "should_subdivide_sharp_curves": True,
                "should_remove_null_curves": True,
            },
            **kwargs,
        )

        # used for scaling via font_size.setter
        self.initial_height = self.height

        if height is None:
            self.font_size = self._font_size

        if self.organize_left_to_right:
            self._organize_submobjects_left_to_right()

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.tex_string)})"

    @property
    def font_size(self):
        """The font size of the tex mobject."""
        return self.height / self.initial_height / SCALE_FACTOR_PER_FONT_POINT

    @font_size.setter
    def font_size(self, font_val):
        if font_val <= 0:
            raise ValueError("font_size must be greater than 0.")
        elif self.height > 0:
            # sometimes manim generates a SingleStringMathex mobject with 0 height.
            # can't be scaled regardless and will error without the elif.

            # scale to a factor of the initial height so that setting
            # font_size does not depend on current size.
            self.scale(font_val / self.font_size)

    def _get_modified_expression(self, tex_string):
        result = tex_string
        result = result.strip()
        result = self._modify_special_strings(result)
        return result

    def _modify_special_strings(self, tex):
        tex = tex.strip()
        should_add_filler = reduce(
            operator.or_,
            [
                # Fraction line needs something to be over
                tex == "\\over",
                tex == "\\overline",
                # Make sure sqrt has overbar
                tex == "\\sqrt",
                tex == "\\sqrt{",
                # Need to add blank subscript or superscript
                tex.endswith("_"),
                tex.endswith("^"),
                tex.endswith("dot"),
            ],
        )

        if should_add_filler:
            filler = "{\\quad}"
            tex += filler

        if tex == "\\substack":
            tex = "\\quad"

        if tex == "":
            tex = "\\quad"

        # To keep files from starting with a line break
        if tex.startswith("\\\\"):
            tex = tex.replace("\\\\", "\\quad\\\\")

        # Handle imbalanced \left and \right
        num_lefts, num_rights = (
            len([s for s in tex.split(substr)[1:] if s and s[0] in "(){}[]|.\\"])
            for substr in ("\\left", "\\right")
        )
        if num_lefts != num_rights:
            tex = tex.replace("\\left", "\\big")
            tex = tex.replace("\\right", "\\big")

        tex = self._remove_stray_braces(tex)

        for context in ["array"]:
            begin_in = ("\\begin{%s}" % context) in tex
            end_in = ("\\end{%s}" % context) in tex
            if begin_in ^ end_in:
                # Just turn this into a blank string,
                # which means caller should leave a
                # stray \\begin{...} with other symbols
                tex = ""
        return tex

    def _remove_stray_braces(self, tex):
        r"""
        Makes :class:`~.MathTex` resilient to unmatched braces.

        This is important when the braces in the TeX code are spread over
        multiple arguments as in, e.g., ``MathTex(r"e^{i", r"\tau} = 1")``.
        """

        # "\{" does not count (it's a brace literal), but "\\{" counts (it's a new line and then brace)
        num_lefts = tex.count("{") - tex.count("\\{") + tex.count("\\\\{")
        num_rights = tex.count("}") - tex.count("\\}") + tex.count("\\\\}")
        while num_rights > num_lefts:
            tex = "{" + tex
            num_lefts += 1
        while num_lefts > num_rights:
            tex = tex + "}"
            num_rights += 1
        return tex

    def _organize_submobjects_left_to_right(self):
        self.sort(lambda p: p[0]) # type: ignore
        return self

    def get_tex_string(self):
        return self.tex_string


class Ypango(Text):
    def __init__(self, text, **pango_kwargs):
        super().__init__(text, **pango_kwargs)
