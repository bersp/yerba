import re
import os
import shutil
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin

from ..utils.aux_functions import better_error_messages


def are_nodes_equal(node1, node2):
    node1_tokens = node1.to_tokens()
    node2_tokens = node2.to_tokens()
    for nt in node1_tokens+node2_tokens:
        nt.map = [0, 0]
    return node1_tokens == node2_tokens


def is_h1(node):
    return node.type == "heading" and node.tag == "h1"


def get_markdownit_nodes(text):
    md = (MarkdownIt("commonmark")
          .use(front_matter_plugin)
          .use(dollarmath_plugin, allow_space=True, double_inline=True))
    return SyntaxTreeNode(md.parse(text))


def handle_includes(text):
    pattern = r"^(>!\s*include\s*\(\s*'([^']+)'\s*\)\s*)$"
    return re.sub(pattern, _include_file_content, text, flags=re.MULTILINE)


def _include_file_content(match):
    filename_to_include = match.group(2)

    _open = better_error_messages(
        custom_msg=(f"An error occurred while including the file "
                    + repr(filename_to_include))
    )(open)
    f = _open(filename_to_include, 'r')
    o = f.read() + "\n"
    f.close()
    return o


def get_slides_md_nodes(md_filename, old_md_filename) -> list[dict]:
    if old_md_filename is None:
        old_text = '#'
    else:
        with open(old_md_filename, "r") as f:
            old_text = f.read()

    with open(md_filename, "r") as f:
        text = f.read()

    text = handle_includes(text)

    nodes = get_markdownit_nodes(text)

    old_nodes = get_markdownit_nodes(old_text)

    old_idx = 0
    old_idx_max = len(tuple(old_nodes))-1  # type: ignore

    idx = 0
    idx_max = len(tuple(nodes))-1  # type: ignore

    slide_number = 0

    slides = []
    d = {'slide_number': slide_number, 'content': []}

    # TODO(bersp): Handle no title in .md or .old.*.md
    while not is_h1(nodes[idx]):
        d['content'].append(nodes[idx])
        idx += 1

    old_front_matter_content = []
    while not is_h1(old_nodes[old_idx]):
        old_front_matter_content.append(old_nodes[old_idx])
        old_idx += 1

    is_new_slide = False
    if idx != old_idx:
        is_new_slide = True
    else:
        for node, old_node in zip(d['content'], old_front_matter_content):
            if not are_nodes_equal(node, old_node):
                is_new_slide = True

    while idx < idx_max:
        node = nodes[idx]
        if is_h1(node):
            if old_idx < old_idx_max and not is_h1(old_nodes[old_idx]):
                is_new_slide = True
                # skip to the next heading
                while (old_idx != old_idx_max and
                       not is_h1(old_nodes[old_idx])):
                    old_idx += 1

            d['is_new_slide'] = is_new_slide
            slides.append(d)

            slide_number += 1
            d = {'slide_number': slide_number, 'title': node, 'content': []}

            if old_idx < old_idx_max:
                is_new_slide = not are_nodes_equal(node, old_nodes[old_idx])
                old_idx += 1
                idx += 1
            else:
                is_new_slide = True
                idx += 1

        elif old_idx > old_idx_max:
            is_new_slide = True
            d['content'].append(node)
            idx += 1

        elif are_nodes_equal(node, old_nodes[old_idx]):
            d['content'].append(node)
            old_idx += 1
            idx += 1
        else:
            is_new_slide = True

            # skip to the next heading
            while (old_idx != old_idx_max and
                   not is_h1(old_nodes[old_idx])):
                old_idx += 1
            while (idx != idx_max and
                   not is_h1(nodes[idx])):
                d['content'].append(nodes[idx])
                idx += 1

    else:
        node = nodes[idx]
        if (idx-idx_max != old_idx-old_idx_max or
                not are_nodes_equal(node, old_nodes[old_idx])):
            is_new_slide = True

    if is_h1(node):
        d['is_new_slide'] = is_new_slide
        slides.append(d)
        slide_number += 1
        d = {'slide_number': slide_number, 'title': node, 'content': []}
    else:
        d['content'].append(nodes[idx])

    d['is_new_slide'] = is_new_slide
    slides.append(d)

    return slides


def get_slides(filename):
    old_filename = os.path.join("./media/", f".old.{filename}")
    if os.path.exists(old_filename):
        for f in os.listdir("./media/slides/"):
            shutil.move(f"./media/slides/{f}", f"./media/old_slides/{f}")
        slides = get_slides_md_nodes(filename, old_filename)
    else:
        slides = get_slides_md_nodes(filename, None)
    return slides
