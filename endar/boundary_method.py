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
        y_min, y_max = -16 * CHUNK, 16 * CHUNK
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

        minecart_icon = ImageMobject(ASSETS_DIR / "minecart.png")
        minecart_icon.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        minecart_icon.set_height(icon_height)
        minecart_icon.move_to(grid.c2p(2 * CHUNK, -11 * CHUNK))

        small_radius = 11
        large_radius = 12

        large_render = Circle(
            radius=large_radius * CHUNK * grid.get_x_unit_size(),
            stroke_width=2,
            color=WHITE,
            fill_color=BLUE_A,
            fill_opacity=0.1,
        ).move_arc_center_to(player_icon.get_center())

        small_render = Circle(
            radius=small_radius * CHUNK * grid.get_x_unit_size(),
            stroke_width=2,
            color=WHITE,
            fill_color=BLUE_A,
            fill_opacity=0.1,
        ).move_arc_center_to(player_icon.get_center())

        annulus = Annulus(
            inner_radius=small_radius * CHUNK * grid.get_x_unit_size(),
            outer_radius=large_radius * CHUNK * grid.get_x_unit_size(),
            stroke_width=0,
            fill_color=RED_B,
            fill_opacity=0.15,
        ).move_arc_center_to(player_icon.get_center())

        player_render = Group(player_icon, small_render)

        self.play(Create(grid))
        self.wait()
        self.play(FadeIn(minecart_icon), FadeIn(player_icon))
        self.wait()
        self.play(Create(large_render), Indicate(minecart_icon, scale_factor=1))
        self.wait()
        self.play(Uncreate(large_render), Create(small_render))
        self.wait()
        self.play(Create(annulus))
        self.wait()

        small_area = (small_radius**2) * PI
        large_area = (large_radius**2) * PI
        annulus_area = math.pi * (large_radius**2 - small_radius**2)

        explored_1 = small_area - 358.14029
        proportion_1 = (explored_1 / annulus_area) * 100

        proportion_1_label = Text(f"{proportion_1:.1f}% explored", color=BLUE_A, font_size=20)
        proportion_1_label.to_edge(UP, buff=0.5)

        self.play(player_render.animate.shift(RIGHT * CHUNK * grid.get_x_unit_size()), FadeIn(proportion_1_label), run_time=2)
        self.wait()

        self.play(FadeOut(proportion_1_label))
        self.play(player_render.animate.shift(UP * CHUNK * grid.get_x_unit_size()), run_time=2)
        self.wait(0.5)
        self.play(player_render.animate.shift(DOWN * 2 * CHUNK * grid.get_x_unit_size()), run_time=2)

        # why  is the old one not appearing??
        # large_render_2 = Circle(
        #     radius=large_radius * CHUNK * grid.get_x_unit_size(),
        #     stroke_width=2,
        #     color=WHITE,
        #     fill_color=BLUE_A,
        #     fill_opacity=0.1,
        # ).move_arc_center_to(player_icon.get_center())

        # explored_2 = 428.39629 - small_area
        # proportion_2 = (explored_2 / annulus_area) * 100

        # proportion_2_label = Text(f"{proportion_2:.1f}% explored", color=BLUE_A, font_size=20)
        # proportion_2_label.to_edge(UP, buff=0.5)

        # self.play(Uncreate(small_render), Create(large_render_2), FadeOut(proportion_1_label), FadeIn(proportion_2_label))
        # self.wait()

        # proportion_3_label = Text("100% explored", color=GREEN_A, font_size=20)
        # proportion_3_label.to_edge(UP, buff=0.5)

        # player_render_2 = Group(player_icon, large_render_2)
        # self.play(player_render_2.animate.shift(LEFT * CHUNK * grid.get_x_unit_size()), FadeOut(proportion_2_label), FadeIn(proportion_3_label), run_time=2)
        # self.wait()


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py {name.capitalize()}")
