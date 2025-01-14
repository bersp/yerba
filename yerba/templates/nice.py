from __future__ import annotations

import numpy as np
from manim import Circle, Difference, Rectangle, VGroup, VMobject

from ..base.template_protocol import PresentationTemplateProtocol
from ..utils.constants import RIGHT, SLIDE_HEIGHT, SLIDE_WIDTH, UP


class PresentationTemplate(PresentationTemplateProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.colors.add_color("ACCENT", "#376A65")

        self.set_main_font(
            regular="Lato-Regular.ttf",
            bold="Lato-Bold.ttf",
            italic="Lato-Italic.ttf",
            bold_italic="Lato-BoldItalic.ttf",
        )

    def background(self) -> VMobject | VGroup:
        def ring(outter_r, inner_r):
            outter_c = Circle(outter_r)
            inner_c = Circle(inner_r)
            d = (
                Difference(outter_c, inner_c)
                .set_fill(opacity=1, color=self.colors.get_color("ACCENT"))
                .set_stroke(width=0)
            )
            return d

        o = VGroup()
        o += Rectangle(
            width=SLIDE_WIDTH,
            height=SLIDE_HEIGHT,
            color=self.colors.get_color("WHITE"),
            fill_opacity=1,
        )

        for _ in range(20):
            x, y = np.random.uniform(2, 6), np.random.uniform(0, 3.5)
            if np.random.rand() > 0.5:
                x, y = x, -y
            else:
                x, y = -x, y
            out_r = np.random.rand()
            inn_r = np.random.uniform(out_r * 0.8, out_r)
            alpha = (1 - out_r) * np.random.uniform(0, 0.5)
            o += ring(out_r, inn_r).move_to(x * RIGHT + y * UP).set_opacity(alpha)

        return o

    def add_title(self, text):
        box = self.get_box("title")

        title_mo = self.text(
            text,
            font_size=self.template_params["title.font_size"],
            color=self.colors.get_color("ACCENT"),
            style=self.template_params["title.style"],
        )

        title_mo.set(box=box)
        self.add(title_mo)

        return title_mo

    def add_subtitle(self, text):
        box = self.get_box("title")

        subtitle_mo = self.text(
            text,
            font_size=self.template_params["subtitle.font_size"],
            color=self.colors.get_color("ACCENT"),
            style=self.template_params["subtitle.style"],
        )

        subtitle_mo.set(box=box)
        self.add(subtitle_mo)

        return subtitle_mo
