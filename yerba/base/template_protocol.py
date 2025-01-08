from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from mdformat.renderer import MDRenderer

from ..utils.latex import YerbaRenderers
from .box import Box
from .slide import Slide

if TYPE_CHECKING:
    from manim import VGroup, VMobject

    from ..managers.color_manager import ColorManager
    from ..managers.id_manager import IDManager
    from .box.named_boxes import NamedBoxes


class PresentationTemplateProtocol(Protocol):
    slide_number: int
    subslide_number: int
    current_slide: "Slide | None"
    template_params: Any
    ids: "IDManager"
    colors: "ColorManager"
    renderer: "MDRenderer"
    yerba_renderers: "YerbaRenderers"

    # Add these for explicit access to QOL methods
    def get_color(self, name: str) -> str:
        ...

    def add_color(self, name: str, value: str) -> None:
        ...

    def new_slide(self, slide_number: int = None) -> "Slide": ...

    def write(self, filename: str) -> None: ...

    def render_md(self, node: Any) -> Any: ...

    @property
    def named_boxes(self) -> "NamedBoxes": ...

    @property
    def tex_template(self) -> Any: ...

    @property
    def linked_positions(self) -> Any: ...

    def background(self) -> "VMobject | VGroup": ...

    def set_main_font(
        self,
        regular: str,
        bold: str,
        italic: str,
        bold_italic: str,
        fonts_path: str = None,
    ) -> None: ...

    def add_cover(
        self, title: str, subtitle: str = None, author: str = None
    ) -> Any: ...

    def add_title(self, text: str) -> Any: ...

    def add_subtitle(self, text: str) -> Any: ...

    def add_footer(self, box: str = "footer") -> Any: ...

    def add_latex_text(self, text: str, box: str = "null", **text_props) -> Any: ...

    def add_latex_math(self, text: str, box: str = "null", **text_props) -> Any: ...

    def add_image(
        self, filename: str, box: str = "active", arrange: str = "hcenter", **img_args
    ) -> Any: ...

    def add_paragraph(
        self, text: str, box: str = "active", **text_props
    ) -> list[Any]: ...

    def normal_codeblock_block(
        self,
        content: str,
        language: str,
        box: str = "active",
        numbers: bool = True,
        font_size: int = 40,
        **args,
    ) -> Any: ...

    def python_yerba_block(self, content: str) -> None: ...

    def md_alternate_block(self, content: str, align: str | None = None) -> None: ...

    def md_fragment_block(self, content: str, **properties) -> None: ...

    def md_overwrite_block(self, content: str, **properties) -> None: ...

    def vspace(self, size: float = 0.25) -> Any: ...

    def do_after_create_new_slide(self, **kwargs) -> None: ...

    def set_box(self, box: str, arrange: str = None) -> None: ...

    def get_box(self, box: str) -> "Box": ...

    def def_grid(self, *args, from_box: str = "active", **kwargs) -> None: ...

    def pause(self, *args, **kwargs) -> None: ...

    def add(
        self,
        mobjects: "VMobject | list[VMobject]",
        idx: int = -1,
        box: "Box | str | None" = None,
    ) -> Any: ...

    def remove(self, mo_or_id: int | "VMobject | list[VMobject]") -> None: ...

    def apply(self, mo_or_id: "VMobject | int", *args, **kwargs) -> Any: ...

    def modify(self, mo_or_id: "VMobject | int", *args, **kwargs) -> Any: ...

    def become(
        self,
        old_mo_or_id: "VMobject | int",
        new_mo_or_id: "VMobject | int",
        *args,
        **kwargs,
    ) -> Any: ...

    def hide(self, mo_or_id: "VMobject | int") -> Any: ...

    def unhide(self, mo_or_id: "VMobject | int") -> Any: ...

    def compute_slide_content(self, node: Any, **f_kwargs) -> list[Any | None]: ...

    def compute_title(self, title: str) -> None: ...

    def compute_inline_command(self, node: Any, **f_kwargs) -> list[None]: ...

    def compute_yerba_block(self, block_type: str, content: str, args: str) -> Any: ...

    def text(self, text: str, box: str = "null", **text_props) -> Any: ...
