from __future__ import annotations

import os
import re
from collections.abc import Iterable
from functools import cached_property
from typing import TYPE_CHECKING, Any
from typing import Union as TypeUnion

import manim
from manim import Rectangle, TexTemplate, VGroup, VMobject
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from mdformat.renderer import MDRenderer
from mdit_py_plugins.dollarmath import dollarmath_plugin

from ..base.properties import funcs_from_props
from ..defaults import yerba_blocks_namedict
from ..logger_setup import logger
from ..managers.color_manager import ColorManager
from ..utils import constants
from ..utils.aux_classes import LinkedPositions
from ..utils.aux_functions import better_error_messages, define_default_kwargs
from ..utils.constants import DOWN, LEFT, ORIGIN, SLIDE_HEIGHT, SLIDE_WIDTH
from ..utils.latex import (
    YerbaRenderers,
    add_font_to_preamble,
    update_tex_enviroment_using_box,
)
from .box import Box, NamedBoxes
from .image import ImagePDFSvg, ImageSvg
from .parser import get_markdownit_nodes
from .slide import Slide
from .template_protocol import PresentationTemplateProtocol
from .ytext import Ycode, Ytex

if TYPE_CHECKING:
    from ..managers.id_manager import IDManager


class PresentationTemplateBase(PresentationTemplateProtocol):
    better_error_messages(
        custom_msg="There seems to be an error initializing the presentation."
    )

    def __init__(
        self, id_manager: IDManager, color_manager: ColorManager, template_params
    ) -> None:
        super().__init__()

        self.slide_number: int = -1
        self.subslide_number: int = 0
        self.current_slide: Slide | None = None

        self.renderer: MDRenderer = MDRenderer()
        self.yerba_renderers: YerbaRenderers = YerbaRenderers()

        self.template_params = template_params

        self.ids = id_manager
        self.colors = color_manager

        # QOL
        self.get_color = self.colors.get_color
        self.add_color = self.colors.add_color

    def new_slide(self, slide_number=None) -> Slide:
        self.ids.reset()
        self.named_boxes.set_current_box("new_slide_default")

        # write last slide before create a new one
        if self.current_slide is not None:
            self.current_slide.write()

        self.named_boxes.remove_all_mobjects()

        if slide_number is None:
            self.slide_number += 1
        else:
            self.slide_number = slide_number

        background = self.background()
        s = Slide(self.slide_number, background=background)
        self.current_slide = s
        self.subslide_number = self.current_slide.subslide_number

        self.do_after_create_new_slide()

        return self.current_slide

    def write(self, filename) -> None:
        if self.current_slide:
            self.current_slide.write()
        os.system(f"rsvg-convert -f pdf -o {filename} ./media/slides/*.svg")

    def render_md(self, node):
        return self.renderer.render(
            node.to_tokens(), {"parser_extension": [self.yerba_renderers]}, {}
        )

    @cached_property
    def named_boxes(self) -> NamedBoxes:
        """Group of named boxes"""
        d = {}
        d["title"] = Box.get_top_box(1.7, arrange="hcenter")
        d["footer"] = Box.get_bottom_box(0.5, arrange="hcenter")
        d["left_margin"] = Box.get_left_box(0.7, arrange="center")
        d["right_margin"] = Box.get_right_box(0.7, arrange="center")
        d["content"] = Box.get_inner_box(
            left_box=d["left_margin"],
            right_box=d["right_margin"],
            top_box=d["title"],
            bottom_box=d["footer"],
            arrange=self.template_params["box.content.arrange"],
        )

        d["full"] = Box.get_full_box(arrange="hcenter")
        d["floating"] = Box.get_full_box(arrange="none")
        m = self.template_params["box.full_with_margins.margins"]
        d["full_with_margins"] = Box.get_full_box(arrange="hcenter").shrink(
            left_gap=m,
            right_gap=m,
            top_gap=m,
            bottom_gap=m,
        )

        nb = NamedBoxes(**d)
        nb.add(
            "new_slide_default",
            getattr(nb, self.template_params["box.new_slide_default"]),
        )
        nb.set_current_box("new_slide_default")

        return nb

    @cached_property
    def tex_template(self):
        tt = TexTemplate(tex_compiler="xelatex", output_format=".xdv")
        tt.add_to_preamble(
            r"""
        \usepackage[no-math]{fontspec}
        \usepackage{ragged2e}
        \usepackage[none]{hyphenat}
        """
            + "\n"
            + self.template_params["add_to_preamble"]
        )
        return tt

    @property
    def linked_positions(self):
        if self.current_slide:
            return self.current_slide.linked_positions
        else:
            raise ValueError("The presentation does not have any slides")

    def background(self) -> VMobject | VGroup:
        return Rectangle(
            width=SLIDE_WIDTH,
            height=SLIDE_HEIGHT,
            color=self.get_color("WHITE"),
            fill_opacity=1,
        )

    def set_main_font(self, regular, bold, italic, bold_italic, fonts_path=None):
        add_font_to_preamble(
            preamble=self.tex_template,
            regular=regular,
            bold=bold,
            italic=italic,
            bold_italic=bold_italic,
            fonts_path=fonts_path,
        )

    @better_error_messages(custom_msg="There seems to be an error creating the cover.")
    def add_cover(self, title, subtitle=None, author=None):
        self.new_slide(slide_number=0)

        box = self.get_box("full")

        cover_mo = VGroup()

        title = self.text(title, style="bold", font_size=50)

        cover_mo += title
        if subtitle is not None:
            cover_mo += self.text(subtitle, font_size=40).next_to(title, DOWN, buff=0.5)

        if author is not None:
            cover_mo += (
                VGroup(
                    self.text("Author", style="bold", font_size=30),
                    self.text(author, font_size=30),
                )
                .arrange(DOWN)
                .next_to(cover_mo, DOWN, buff=2.5)
            )

        cover_mo.move_to(ORIGIN)

        cover_mo.set(box=box)
        self.add(cover_mo)

        return cover_mo

    @better_error_messages()
    def add_title(self, text):
        box = self.get_box("title")

        title_mo = self.text(
            text,
            font_size=self.template_params["title.font_size"],
            color=self.template_params["title.color"],
            style=self.template_params["title.style"],
        )

        title_mo.set(box=box)
        self.add(title_mo)

        return title_mo

    @better_error_messages()
    def add_subtitle(self, text):
        box = self.get_box("title")

        subtitle_mo = self.text(
            text,
            font_size=self.template_params["subtitle.font_size"],
            color=self.template_params["subtitle.color"],
            style=self.template_params["subtitle.style"],
        )

        subtitle_mo.set(box=box)
        self.add(subtitle_mo)

        return subtitle_mo

    def add_footer(self, box="footer"):
        if self.slide_number == 0:  # no footer in the cover slide
            return

        box = self.get_box("footer").set_arrange("none")

        footer_mo = (
            self.text(str(self.slide_number), color=self.get_color("DARK_GRAY"))
            .move_to(box.get_right())
            .shift(1 / 2 * LEFT)
        )

        footer_mo.set(box=box)
        self.add(footer_mo)

        return footer_mo

    # -- specialized functions (you probably don't want to modify these)

    def add_latex_text(self, text, box="null", **text_props):
        funcs, text_props = funcs_from_props(text_props, only_custom_props=True)

        text_props = define_default_kwargs(
            text_props,
            tex_template=self.tex_template,
            tex_environment="justify",
            font_size=self.template_params["text.font_size"],
            color=self.template_params["text.color"],
        )

        box = self.get_box(box)

        text_props["tex_template"] = update_tex_enviroment_using_box(
            box,
            text_props["font_size"],
            text_props["tex_template"],
        )

        text_mo = Ytex(text, subslide_number=self.subslide_number, **text_props)

        predefined_box = getattr(text_mo, "box", None)
        if predefined_box is None:
            text_mo.set(box=box)
        else:
            text_mo.set(box=self.get_box(predefined_box))

        for f in funcs:
            f(text_mo)

        self.add(text_mo)

        return text_mo

    def add_latex_math(self, text, box="null", **text_props):
        funcs, text_props = funcs_from_props(text_props, only_custom_props=True)
        text_props = define_default_kwargs(
            text_props,
            tex_template=self.tex_template,
            tex_environment="align*",
            font_size=self.template_params["math.font_size"],
            color=self.template_params["math.color"],
        )

        box = self.get_box(box)

        math_mo = Ytex(text, subslide_number=self.subslide_number, **text_props)

        predefined_box = getattr(math_mo, "box", None)
        box_arrange = getattr(math_mo, "box_arrange", None)
        if predefined_box is None:
            math_mo.set(box=box, box_arrange=box_arrange or "hcenter")
        else:
            math_mo.set(box=self.get_box(predefined_box))

        for f in funcs:
            f(math_mo)

        self.add(math_mo)

        return math_mo

    def add_image(self, filename, box="active", arrange="hcenter", **img_args):
        funcs, img_args = funcs_from_props(img_args, only_custom_props=True)

        box = self.get_box(box)

        if filename.split(".")[-1].lower() == "pdf":
            img_mo = ImagePDFSvg(filename, **img_args)
        else:
            img_mo = ImageSvg(filename, **img_args)

        img_mo = img_mo.set(box=box, box_arrange=arrange)
        self.add(img_mo)

        for f in funcs:
            f(img_mo)

        return img_mo

    @better_error_messages()
    def add_paragraph(self, text, box="active", **text_props) -> list[VMobject]:
        tokens = (
            MarkdownIt("commonmark")
            .use(dollarmath_plugin, allow_space=True, double_inline=True)
            .parse(text)
        )
        nodes = SyntaxTreeNode(tokens)[0]

        box = self.get_box(box)

        if nodes.type == "math_block":
            t = self.render_md(nodes)[2:-3].strip()
            return [self.add_latex_math(t, box=box, **text_props)]
        else:
            nodes = nodes[0]

        mo_list = []
        acc_text = ""
        for node in nodes:  # type: ignore
            if node.type == "math_inline_double":
                acc_text = acc_text.strip()
                if acc_text:
                    mo = self.add_latex_text(acc_text, box=box, **text_props)
                    mo_list.append(mo)
                acc_text = ""

                t = self.render_md(node)
                mo = self.add_latex_math(t[2:-3], box=box, **text_props)
                mo_list.append(mo)
            elif node.type == "softbreak":
                pass
            else:
                acc_text += self.render_md(node)
        if acc_text:
            mo = self.add_latex_text(acc_text, box=box, **text_props)
            mo_list.append(mo)

        return mo_list

    @better_error_messages(custom_msg="An error was found in a codeblock")
    def normal_codeblock_block(
        self, content, language, box="active", numbers=True, font_size=40, **args
    ):
        style = [
            r"commentstyle=\color{codegreen}",
            r"keywordstyle=\color{codeblue}",
            r"numberstyle=\tiny\color{codegray}",
            r"stringstyle=\color{codeblue}",
            r"basicstyle=\ttfamily\footnotesize\color{codeblack}",
            r"breakatwhitespace=false",
            r"breaklines=true",
            r"captionpos=b",
            r"keepspaces=true",
            r"numbersep=5pt",
            r"showspaces=false",
            r"showstringspaces=false",
            r"showtabs=false",
            r"tabsize=2",
        ]
        if numbers:
            style.append("numbers=left")

        tt = self.tex_template.copy()
        green = self.get_color("GREEN").replace("#", "")
        blue = self.get_color("BLUE").replace("#", "")
        gray = self.get_color("GRAY").replace("#", "")
        black = self.get_color("BLACK").replace("#", "")
        purple = self.get_color("PURPLE").replace("#", "")
        tt.add_to_preamble(
            r"""
            \usepackage{listings}
            \usepackage{xcolor}
            """
            + rf"""
            \definecolor{{codeblack}}{{HTML}}{{{black}}}
            \definecolor{{codegray}}{{HTML}}{{{gray}}}
            \definecolor{{codegreen}}{{HTML}}{{{green}}}
            \definecolor{{codeblue}}{{HTML}}{{{blue}}}
            \definecolor{{codepurple}}{{HTML}}{{{purple}}}
            """
            + rf"""
            \lstdefinestyle{{style}}{{{",".join(style)}}}
            \lstset{{style=style}}
            """
        )
        tt.add_to_preamble(rf"\lstset{{language={language.title()}}}")

        text_props: dict[str, Any] = dict(
            tex_template=tt,
            tex_environment="lstlisting",
            font_size=font_size,
        )

        box = self.get_box(box)

        text_props["tex_template"] = update_tex_enviroment_using_box(
            box,
            text_props["font_size"],
            text_props["tex_template"],
        )

        code_mo = Ycode(content, **text_props)
        code_mo.set(box=box)

        self.add(code_mo)

        return code_mo

    def python_yerba_block(self, content):
        content = (
            "locals().update(vars(constants))\n"
            "locals().update(ColorManager().colors)\n"
            "locals().update(vars(manim))\n"
        ) + content
        exec(content)

    @better_error_messages(
        custom_msg="An error was found in a md_alternate yerba block"
    )
    def md_alternate_block(self, content: str, align: str | None = None):
        nodes = get_markdownit_nodes(content)

        null_box = self.get_box("null")
        content_mo_list = []
        content_mo = []
        for node in nodes:  # type: ignore
            if node.type == "hr":
                content_mo_list.append(content_mo)
                content_mo = []
            else:
                mo_list = self.compute_slide_content(node, box=null_box)
                content_mo += mo_list
        content_mo_list.append(content_mo)

        content_mo_list = list(filter(None, content_mo_list))

        self.add(content_mo_list[0], box="active")

        vg_track = VGroup(*content_mo_list[0])
        for ii in range(len(content_mo_list) - 1):
            self.pause()
            self.remove(content_mo_list[ii])

            box_copy = Box.from_box(self.get_box("active"))
            self.add(content_mo_list[ii + 1], box=box_copy)
            self.linked_positions.append(
                LinkedPositions(
                    source=content_mo_list[ii + 1],
                    destination=vg_track,
                    align=align or box_copy.arrange,
                )
            )
            box_copy.auto_arrange()
            box_copy.set_arrange("none")

    @better_error_messages(custom_msg="An error was found in a md_fragment yerba block")
    def md_fragment_block(self, content, *args, **properties):
        nodes = get_markdownit_nodes(content)

        assert len(args) == 0, "Fragment blocks only accept keyword arguments"

        for node in nodes:  # type: ignore
            self.compute_slide_content(node, **properties)

    @better_error_messages(
        custom_msg="An error was found in a md_overwrite yerba block"
    )
    def md_overwrite_block(self, content, *args, **properties):
        if len(args) < 1:
            raise ValueError("The first argument must be a previously defined id")
        id = args[0]
        original_mo_l = self.ids.get(id)

        nodes = get_markdownit_nodes(content)

        if "box" in properties:
            box_copy = self.get_box(properties.pop("box"))
        elif hasattr(original_mo_l[0], "box"):
            box_copy = Box.from_box(original_mo_l[0].box)
        else:
            box_copy = self.get_box("floating")

        if "align" in properties:
            align = properties.pop("align")
        else:
            align = box_copy.arrange

        new_mo_l = []
        self.remove(original_mo_l)
        for node in nodes:  # type: ignore
            mo_l = self.compute_slide_content(node, box=box_copy, **properties)
            mo_l = list(filter(None, mo_l))
            new_mo_l += mo_l
            self.ids.add(id, mo_l)
        box_copy.auto_arrange()

        self.linked_positions.append(
            LinkedPositions(
                source=new_mo_l, destination=VGroup(*original_mo_l), align=align
            )
        )

    def vspace(self, size=0.25):
        box = self.get_box("active")

        vspace_mo = (
            Rectangle(height=size, width=box.width)
            .set_stroke(opacity=0)
            .set(fill_opacity=0)
        )
        vspace_mo.set(box=box)
        self.add(vspace_mo)

        return vspace_mo

    def do_after_create_new_slide(self, **kwargs):
        kwargs = define_default_kwargs(kwargs, add_footer=False)
        if self.template_params["add_footer"]:
            self.add_footer()

    # -- box methods

    def set_box(self, box, arrange=None):
        box = self.get_box(box)
        if arrange is not None:
            box.arrange = arrange
        self.named_boxes.set_current_box(box)

    def get_box(self, box) -> Box:
        err_msg = f"{box!r} is not a named box or a box instance"
        if isinstance(box, Box):
            return box
        elif box == "null":
            return Box.get_null_box()
        elif isinstance(box, str):
            pos, *grid_idx = box.split(".")
            if hasattr(self.named_boxes, pos):
                box = getattr(self.named_boxes, pos)
            else:
                raise ValueError(err_msg)

            if grid_idx:
                return box[grid_idx[0]]
            else:
                return box
        else:
            raise ValueError(err_msg)

    def def_grid(self, *args, from_box="active", **kwargs):
        box = self.get_box(box=from_box)
        g = box.def_grid(*args, **kwargs)

        for subgrid_name, subgrid_box in g.items():
            self.named_boxes.add(subgrid_name, subgrid_box)

    # -- slide methods

    def _apply_func_to_mobject(
        self,
        mobject,
        funcs,
        position="original",
        transfer_id=None,
        f_args=None,
        f_kwargs=None,
    ) -> VMobject:
        """
        Apply a function or a list of functions to a VMobject.

        Parameters
        ----------
        mobject : VMobject
            The VMobject to modify.
        funcs : callable or list of callable
            The function or list of functions to apply to the VMobject.
        position : str, optional
            Specifies where the modified VMobject should be positioned.
        f_args : list, optional
            Positional arguments for the functions.
        f_kwargs : dict, optional
            Keyword arguments for the functions.

        Returns
        -------
        VMobject
            The modified VMobject.
        """
        if self.current_slide is None:
            raise ValueError("The presentation does not have any slides")

        if f_args is None:
            f_args = []
        if f_kwargs is None:
            f_kwargs = {}

        if mobject.origin_subslide_number == self.subslide_number:
            modified_mobject = mobject
        else:
            modified_mobject = mobject.copy()
            if transfer_id:
                self.ids.replace(transfer_id, old=mobject, new=modified_mobject)

        if callable(funcs):
            funcs(modified_mobject, *f_args, **f_kwargs)
        elif isinstance(funcs, Iterable):
            for f in funcs:
                f(modified_mobject, *f_args, **f_kwargs)
        else:
            raise TypeError("'func' must be callable or list of callables")

        if mobject.origin_subslide_number != self.subslide_number:
            self.current_slide._replace_from_last_subslide(mobject, modified_mobject)
            if position == "original":
                self.current_slide.linked_positions.append(
                    LinkedPositions(
                        source=modified_mobject, destination=mobject, align="center"
                    )
                )
            elif position == "modified":
                mobject.box.replace(mobject, modified_mobject)
                self.current_slide.linked_positions.append(
                    LinkedPositions(
                        source=mobject, destination=modified_mobject, align="center"
                    )
                )
            elif position == "independent":
                pass
            else:
                raise ValueError(
                    f"'position' must be 'original', 'modified' or 'independent' not {repr(position)}"
                )

        return modified_mobject

    def _modify_mobject_props(self, mobject, transfer_id=None, **props) -> VMobject:
        """
        Modify properties of a mobject,

        Parameters
        ----------
        mobject : mobject(s)
            The mobject to modify.
        **props
            Properties to modify.
        """
        funcs, _ = funcs_from_props(props)

        modified_mobject = self._apply_func_to_mobject(
            mobject=mobject,
            funcs=funcs,
            transfer_id=transfer_id,
        )
        return modified_mobject

    def pause(self, *args, **kwargs):
        if self.current_slide is None:
            raise ValueError("The presentation does not have any slides")
        self.current_slide.add_new_subslide(*args, **kwargs)
        self.subslide_number = self.current_slide.subslide_number
        return None

    def add(
        self,
        mobjects: VMobject | list[VMobject],
        idx: int = -1,
        box: Box | str | None = None,
    ):
        if self.current_slide is None:
            raise ValueError("The presentation does not have any slides")

        if not isinstance(mobjects, list):
            mobjects = [mobjects]

        if box is None:
            for mo in mobjects:
                if not hasattr(mo, "box"):
                    mo.set(box=self.get_box("active"))
        else:
            for mo in mobjects:
                mo.set(box=self.get_box(box))

        return self.current_slide.add_to_subslide(mobjects, idx)

    def remove(self, mo_or_id: int | VMobject | list[VMobject]):
        if self.current_slide is None:
            raise ValueError("The presentation does not have any slides")
        if isinstance(mo_or_id, int):
            self.current_slide.remove_from_subslide(self.ids.get(mo_or_id))
        else:
            return self.current_slide.remove_from_subslide(mo_or_id)

    def apply(self, mo_or_id: VMobject | int, *args, **kwargs):
        if isinstance(mo_or_id, int):
            return [
                self._apply_func_to_mobject(mo, *args, **kwargs)
                for mo in self.ids.get(mo_or_id)
            ]
        else:
            return self._apply_func_to_mobject(mo_or_id, *args, **kwargs)

    def modify(self, mo_or_id: VMobject | int, *args, **kwargs):
        if isinstance(mo_or_id, int):
            return [
                self._modify_mobject_props(mo, transfer_id=mo_or_id, *args, **kwargs)
                for mo in self.ids.get(mo_or_id).copy()
            ]
        else:
            return self._modify_mobject_props(mo_or_id, *args, **kwargs)

    def become(
        self,
        old_mo_or_id: VMobject | int,
        new_mo_or_id: VMobject | int,
        *args,
        **kwargs,
    ):
        """
        TODO: This function need a refactor.
        """
        if self.current_slide is None:
            raise ValueError("The presentation does not have any slides")

        if isinstance(old_mo_or_id, int):
            old = self.ids.get(old_mo_or_id)[0]
        else:
            old = old_mo_or_id
        if isinstance(new_mo_or_id, int):
            new = self.ids.get(new_mo_or_id)[0]
        else:
            new = new_mo_or_id

        if "position" in kwargs:
            kwargs["position"] = {
                "original": "original",
                "modified": "modified",
                "old": "original",
                "new": "modified",
            }[kwargs["position"]]

        new.set(origin_subslide_number=self.subslide_number)
        return self._apply_func_to_mobject(
            old, lambda old, new: old.become(new), f_args=[new], *args, **kwargs
        )

    def hide(self, mo_or_id: VMobject | int):
        return self.modify(mo_or_id, hide=True)

    def unhide(self, mo_or_id: VMobject | int):
        return self.modify(mo_or_id, hide=False)

    # -- high level computations

    def compute_slide_content(
        self, node, **f_kwargs
    ) -> TypeUnion[list[VMobject], list[VMobject | None]]:
        if node.type == "heading":
            if node.tag == "h2":
                subtitle = node.children[0].content
                return [self.add_subtitle(text=subtitle)]
            else:
                logger.error(f"{node.tag} is not implemented in the parser")
                quit()
        elif node.type == "paragraph" or node.type == "math_block":
            paragraph = self.render_md(node)
            return self.add_paragraph(text=paragraph, **f_kwargs)
        elif node.type == "blockquote":
            return self.compute_inline_command(node, **f_kwargs)
        elif node.type == "fence" and node.tag == "code":
            m = re.match(r"([a-zA-Z\s]+)(?:\s*\((.*)\))?$", node.info)
            if m is None:
                logger.error(
                    f"There is a syntax error in '[blue]{node.info}[/blue]'",
                    extra={"markup": True, "highlighter": None},
                )
                quit()
            node_name, args = m.groups()
            node_name = node_name.strip()
            for block_type, names in yerba_blocks_namedict.items():
                if node_name in names:
                    return [self.compute_yerba_block(block_type, node.content, args)]
            else:
                if args:
                    args = f"language='{node_name}'," + args
                else:
                    args = f"language='{node_name}',"
                return [
                    self.compute_yerba_block("normal_codeblock", node.content, args)
                ]
        elif node.type == "html_block" or node.type == "code_block":
            return [None]
        else:
            logger.error(f"{node.type} type is not implemented in the parser")
            quit()

    def compute_title(self, title):
        if not title or title.lower() == "notitle":
            self.set_box(box="full_with_margins")
        else:
            self.add_title(text=title)

    def compute_inline_command(self, node, **f_kwargs) -> list[VMobject | None]:
        globals().update(vars(constants))
        globals().update(ColorManager().colors)
        globals().update(vars(manim))

        def _exec_inline_command(self, command, str_args, f_kwargs=None):
            f_kwargs = f_kwargs or {}
            if str_args:
                return eval(f"self.{command}({str_args}, **f_kwargs)")
            else:
                return eval(f"self.{command}()")

        if node.children:
            text = node.children[0].children[0].content
        else:
            return [None]

        out = []
        for t in text.split("\n"):
            m_python_command = re.search(r"! `(.*)`", t)
            m_yerba_command = re.match(r"^!\s*([a-zA-Z\s]+)(?:\s*\((.*)\))?$", t)

            if m_yerba_command:
                command, str_args = m_yerba_command.groups()
                command = command.strip().replace(" ", "_")
                exec_inline_command = better_error_messages(custom_msg=f">{t}")(
                    _exec_inline_command
                )
                out.append(exec_inline_command(self, command, str_args, f_kwargs))

            elif m_python_command:
                f = better_error_messages(custom_msg=f">{t}")(lambda self, c: exec(c))
                out.append(f(self, c=m_python_command.group(1)))

        return out

    def compute_yerba_block(self, block_type: str, content: str, args: str):
        if args:
            return eval(f"self.{block_type}_block(content, {args})")
        else:
            return eval(f"self.{block_type}_block(content)")

    # -- QOL functions

    def text(self, text, box="null", **text_props):
        return self.add_paragraph(text, box=box, **text_props)[0]

    mod = modify
    app = apply
    bec = become
