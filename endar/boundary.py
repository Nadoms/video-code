import json
import numpy as np
import math
from manim import *
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"


class Plot(Scene):

    def construct(self):
        # Theme
        Text.set_default(font="Minecraft")

        CHUNK = 16
        y_min, y_max = -20 * CHUNK, 20 * CHUNK
        step = CHUNK
        y_span = y_max - y_min
        x_span = (config.frame_width / config.frame_height) * y_span
        x_half = x_span / 2

        grid = NumberPlane(
            x_range=[-x_half, x_half, step],
            y_range=[y_min, y_max, step],
            x_length=config.frame_width,
            y_length=config.frame_height,
            background_line_style={
                "stroke_color": GREY_B,
                "stroke_width": 1,
                "stroke_opacity": 0.6,
            },
            axis_config={
                "stroke_opacity": 0,
            },
        )

        icon_height = 0.5

        player_icon = ImageMobject(ASSETS_DIR / "steve.png")
        player_icon.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        player_icon.set_height(icon_height)

        brute_icon = ImageMobject(ASSETS_DIR / "brute.png")
        brute_icon.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        brute_icon.set_height(icon_height)
        brute_icon.move_to(grid.c2p(5 * CHUNK, 15 * CHUNK))

        circle = Circle(
            radius=13 * CHUNK * grid.get_x_unit_size(),
            stroke_width=2,
            color=WHITE,
            fill_color=BLUE_A,
            fill_opacity=0.1,
        ).move_arc_center_to(player_icon.get_center())

        player_render = Group(circle, player_icon)

        self.play(Create(grid))
        self.wait()
        self.play(Create(circle), FadeIn(player_icon))
        self.wait()
        self.play(FadeIn(brute_icon))
        self.wait()
        self.play(player_render.animate.move_to(grid.c2p(0, 3 * CHUNK)), run_time=2)

        self.wait()

        arc = Arc(
            radius=13 * CHUNK * grid.get_x_unit_size(),
            start_angle=0,
            angle=0.5 * TAU,
            stroke_width=2,
            color=YELLOW,
        ).move_arc_center_to(player_icon.get_center())

        self.play(Create(arc), FadeOut(circle), FadeOut(brute_icon))
        self.play(Indicate(arc, scale_factor=1))
        self.wait()


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py {name.capitalize()}")
