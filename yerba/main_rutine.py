from __future__ import annotations

import importlib
import os
import shutil
from typing import TYPE_CHECKING

import yaml

from .base.parser import get_slides
from .defaults import parser_params, template_params
from .logger_setup import logger
from .managers.color_manager import ColorManager
from .managers.id_manager import IDManager
from .utils.aux_functions import (
    better_error_messages,
    check_dependencies,
    create_folder_structure,
)

if TYPE_CHECKING:
    from .base.template import PresentationTemplateBase


better_error_messages(custom_msg="There seems to be an error loading the template.")


def make_presentation_from_template(template_name, custom_template_name):
    inh_bases = []

    if custom_template_name is not None:
        try:
            ct = importlib.import_module(custom_template_name)
        except ModuleNotFoundError:
            raise Exception(f"No template named {repr(custom_template_name)}")

        pct = getattr(ct, "PresentationTemplate", None)
        if pct is None:
            logger.error(
                f"'PresentationTemplate' is not defined in {repr(custom_template_name)}"
            )
        else:
            inh_bases.append(pct)

    if os.path.exists(template_name + ".py"):
        mod = (template_name,)
    else:
        mod = (f".templates.{template_name}", "yerba")
    try:
        t = importlib.import_module(*mod)
    except ModuleNotFoundError:
        raise Exception(f"No template named {template_name!r}")

    pt = getattr(t, "PresentationTemplate", None)
    if pt is None:
        logger.error(f"'PresentationTemplate' is not defined in {template_name!r}")
        quit()
    else:
        inh_bases.append(pt)

    return type("Presentation", tuple(inh_bases), {})


@better_error_messages(custom_msg="There seems to be an error in the medatada.")
def process_metadata(metadata, parser_params, template_params):
    if "parser_params" in metadata:
        parser_params.update(metadata["parser_params"])

    if "template_params" in metadata:
        template_params.update(metadata["template_params"])

    if "colors" in metadata:
        ColorManager().add_multiple_colors(metadata.pop("colors"))

def clean_old_slides_folder_and_generate_dot_old_file(filename):
    for f in os.listdir("./media/old_slides/"):
        os.remove(f"./media/old_slides/{f}")
    shutil.copyfile(filename, f"./media/.old.{filename}")


class MainRutine:
    def __init__(self, input_filename) -> None:
        logger.info(
            "Initializing [green]Yerba[/green] "
            "—[i]Built on [green]Manim Community[/green][/i]—",
            extra={"markup": True, "highlighter": None},
        )

        check_dependencies()
        create_folder_structure()

        self.input_filename: str = input_filename
        self.cover_metadata: dict | None = None

        self.slides: list[dict] = get_slides(input_filename)

        self.template_name: str = "nice"
        self.custom_template_name: str | None = None

    @staticmethod
    def use_backup_slide(slide_number):
        os.system(
            f"find ./media/old_slides/ | grep -i 's{slide_number:04g}_'"
            " | xargs mv -t ./media/slides/"
        )

    def compute_front_matter(self, node):
        metadata = yaml.safe_load(node.content)

        process_metadata(metadata, parser_params, template_params)

        if "cover" in metadata:
            self.cover_metadata = metadata.pop("cover")

        if "template" in metadata:
            self.template_name = metadata.pop("template")

        if "custom_template" in metadata:
            self.custom_template_name = metadata.pop("custom_template")

    def initialize_presentation(self) -> PresentationTemplateBase:
        Presentation = make_presentation_from_template(
            template_name=self.template_name,
            custom_template_name=self.custom_template_name,
        )
        self.output_filename = str(os.path.splitext(self.input_filename)[0]) + ".pdf"

        p = Presentation(
            id_manager=IDManager(),
            color_manager=ColorManager(),
            template_params=template_params,
        )
        return p

    def run(self):
        slide0 = self.slides[0]

        if slide0["is_new_slide"]:
            parser_params["only_calculate_new_slides"] = False
            logger.info(
                "[yellow b]Reading[/yellow b] configuration",
                extra={"markup": True, "highlighter": None},
            )
        else:
            slide0["is_new_slide"] = True
            logger.info(
                "[yellow]Loading[/yellow] configuration",
                extra={"markup": True, "highlighter": None},
            )

        if slide0["content"] and slide0["content"][0].type == "front_matter":
            node = self.slides[0]["content"].pop(0)
            self.compute_front_matter(node)

        # Create Presentation
        self.p = self.initialize_presentation()

        if self.cover_metadata is not None:
            self.p.add_cover(**self.cover_metadata)

        for n, slide in enumerate(self.slides):
            slide_number = slide["slide_number"]
            self.p.slide_number = slide_number

            if (
                parser_params["only_calculate_new_slides"]
                and not slide["is_new_slide"]
                and n != 0
            ):
                self.use_backup_slide(slide_number)
                title = slide["title"].children[0].content
                logger.info(
                    rf"[yellow]Loading backup[/yellow] of Slide {slide_number} ([u]{title}[/u])",
                    extra={"markup": True, "highlighter": None},
                )
                continue

            if n != 0:
                title = slide["title"].children[0].content
                logger.info(
                    rf"[yellow b]Generating[/yellow b] Slide {slide_number} ([u]{title}[/u])",
                    extra={"markup": True, "highlighter": None},
                )
                self.p.new_slide(slide_number)
                self.p.compute_title(title)

            for node in slide["content"]:
                self.p.compute_slide_content(node)

        self.p.write(self.output_filename)

        clean_old_slides_folder_and_generate_dot_old_file(self.input_filename)

        logger.info(
            "[green b]Ready[/green b]", extra={"markup": True, "highlighter": None}
        )
