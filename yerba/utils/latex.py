import os
import re
import pkg_resources

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from mdformat.renderer._context import make_render_children

from ..utils.constants import SLIDE_WIDTH
from ..managers.color_manager import ColorManager


def parse_props(props: str):
    from ..utils import constants
    locals().update(vars(constants))
    locals().update(ColorManager().colors)
    props = (props.replace(r"%20", r" ")
                  .replace(r"%22", r'"')
                  .replace(r"%5B", r"[")
                  .replace(r"%5D", r"]"))
    return eval(f"dict({props})")


def paragraph_to_md_nodes(text):
    mdparse = (MarkdownIt("commonmark", {"breaks": True})
               .disable(["emphasis"])
               .parse(text))
    if not mdparse:
        return None

    inlines_nodes = SyntaxTreeNode(mdparse).children[0].children[0].children

    return inlines_nodes


def markdown_to_manim_text_and_props(md_nodes):
    props = []
    idx_submo = []
    out_text = ""

    soft_brake_state = 0

    ii = 0
    for node in md_nodes:
        if node.type == "text":
            out_text += node.content

            # increment ii only if the last node was a 'softbreak'
            # and the previous one a modified text ('link')
            if soft_brake_state <= 0:
                ii += 1
            soft_brake_state = 0

        # handle substrings with props
        elif node.type == "link":
            pl = node.attrs['href']
            props.append(parse_props(pl))

            idx_submo.append(ii)
            ii += 1

            out_text += "{{" + node.children[0].content + "}}"

            soft_brake_state = -1

        elif node.type == "softbreak":
            out_text += " "
            soft_brake_state += 1

        else:
            raise ValueError(
                f"nodes of type {node.type} are not implemented in the parser"
            )

    return out_text, idx_submo, props


def process_enhanced_text(text):
    # check if the text finish with [-](<props>)
    m = re.search(r"\[\-\]\(([^]]+)\)\s*$", text)
    if m:
        text = text.replace(m.group(0), "")
        general_props = parse_props(m.group(1))
    else:
        general_props = {}

    md_nodes = paragraph_to_md_nodes(text)
    manim_text, idx_submo, props = markdown_to_manim_text_and_props(md_nodes)
    ismo_props_zip = zip([-1]+idx_submo, [general_props]+props)

    return manim_text, ismo_props_zip


class YerbaRenderers:
    """This a class to parse markdown_it nodes with mdformat"""
    def __init__(self):
        self.RENDERERS = {
            "em": self.em,
            "strong": self.strong,
            "code_inline": self.code_inline,
            "math_inline": lambda s, _: f"${s.content}$",
            "math_inline_double": lambda s, _: f"$${s.content}$$",
            "math_block": lambda s, _: f"$${s.content}$$",
        }

    def em(self, node, context) -> str:
        text = make_render_children(separator="")(node, context)
        return fr"\textit{{{text}}}"

    def strong(self, node, context) -> str:
        text = make_render_children(separator="")(node, context)
        return fr"\textbf{{{text}}}"

    def code_inline(self, node, _) -> str:
        code = node.content
        return fr"\verb|{code}|"

# ---


def add_font_to_preamble(preamble, regular, bold, italic, bold_italic,
                         fonts_path=None):

    if fonts_path is None:
        yerba_font_path = pkg_resources.resource_filename(
            __name__, '../templates/fonts/')
        yerba_regular_font_path = os.path.join(yerba_font_path, regular)
        if os.path.exists(yerba_regular_font_path):
            fonts_path_str = f"Path = {yerba_font_path}"
        else:
            fonts_path_str = ""
    else:
        fonts_path_str = f"Path = {fonts_path}"

    t = f"""
    \n\\setmainfont[
        {fonts_path_str},
        BoldFont = {bold},
        ItalicFont = {italic},
        BoldItalicFont = {bold_italic},
    ]{{{regular}}}\n
    """

    preamble.add_to_preamble(t)


def update_tex_enviroment_using_box(box, font_size, tex_template, xmargin=0):
    tex_template = tex_template.copy()
    pt = box.width/SLIDE_WIDTH * 24/font_size * (820-xmargin)
    tex_template.add_to_preamble(fr"""
        \usepackage{{geometry}}
        \geometry{{papersize={{{pt}pt, 20cm}}}}
    """)
    return tex_template
