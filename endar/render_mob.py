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
        y_min, y_max = -64 * CHUNK, 64 * CHUNK
        step = CHUNK
        y_span = y_max - y_min
        x_span = (config.frame_width / config.frame_height) * y_span
        x_half = x_span / 2

        grid = NumberPlane(
            x_range=[-x_half, x_half, 8 * step],
            y_range=[y_min, y_max, 8 * step],
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

        grid_hd = NumberPlane(
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
        player_icon.move_to(grid.c2p(-48 * CHUNK, 0))

        guardian_icon = ImageMobject(ASSETS_DIR / "elder_guardian.png")
        guardian_icon.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        guardian_icon.set_height(icon_height)

        circle = Circle(
            radius=32 * CHUNK * grid.get_x_unit_size(),
            stroke_width=2,
            color=WHITE,
            fill_color=BLUE_A,
            fill_opacity=0.1,
        ).move_arc_center_to(player_icon.get_center())
        render_label = Text("32 chunk radius", color=BLUE, font_size=24)
        render_label.next_to(circle, direction=UP)

        player_render = Group(circle, player_icon)
        dots = VGroup()

        self.play(Create(grid))
        self.wait()
        self.play(FadeIn(guardian_icon))
        self.wait()
        self.play(Create(circle), FadeIn(player_icon))
        self.wait()
        self.play(Write(render_label))
        self.wait()
        self.play(FadeOut(render_label))
        self.wait()
        self.play(player_render.animate.move_to(grid.c2p(-32 * CHUNK, 0)), run_time=2)

        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        ao = (math.sqrt(32 ** 2 / 2))

        self.wait()
        self.play(player_render.animate.move_to(grid.c2p(-32 * CHUNK, 32 * CHUNK)), run_time=0.5)
        self.play(player_render.animate.move_to(grid.c2p(-ao * CHUNK, ao * CHUNK)), run_time=2)
        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        self.wait()
        self.play(player_render.animate.move_to(grid.c2p(0, 48 * CHUNK)), run_time=0.5)
        self.play(player_render.animate.move_to(grid.c2p(0, 32 * CHUNK)), run_time=2)
        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        self.wait()
        self.play(player_render.animate.move_to(grid.c2p(32 * CHUNK, 32 * CHUNK)), run_time=0.2)
        self.play(player_render.animate.move_to(grid.c2p(ao * CHUNK, ao * CHUNK)), run_time=0.5)
        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        self.play(player_render.animate.move_to(grid.c2p(48 * CHUNK, 0)), run_time=0.2)
        self.play(player_render.animate.move_to(grid.c2p(32 * CHUNK, 0)), run_time=0.5)
        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        self.play(player_render.animate.move_to(grid.c2p(32 * CHUNK, -32 * CHUNK)), run_time=0.2)
        self.play(player_render.animate.move_to(grid.c2p(ao * CHUNK, -ao * CHUNK)), run_time=0.5)
        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        self.play(player_render.animate.move_to(grid.c2p(0, -48 * CHUNK)), run_time=0.2)
        self.play(player_render.animate.move_to(grid.c2p(0, -32 * CHUNK)), run_time=0.5)
        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        self.play(player_render.animate.move_to(grid.c2p(-32 * CHUNK, -32 * CHUNK)), run_time=0.2)
        self.play(player_render.animate.move_to(grid.c2p(-ao * CHUNK, -ao * CHUNK)), run_time=0.5)
        self.add(dots.add(Dot(player_icon.get_center(), radius=0.05, color=YELLOW)), player_render)

        self.wait()

        guardian_circle = Circle(
            radius=32 * CHUNK * grid.get_x_unit_size(),
            stroke_width=2,
            color=RED,
            fill_color=RED,
            fill_opacity=0.1,
        ).move_arc_center_to(guardian_icon.get_center())

        self.play(FadeOut(player_render))

        guardian_dotted = DashedVMobject(guardian_circle.copy(), num_dashes=24, dashed_ratio=0.4, fill_opacity=0)

        self.play(Create(guardian_dotted))
        self.wait()
        self.play(Transform(guardian_dotted, guardian_circle))
        self.remove(guardian_dotted)
        self.add(guardian_circle)

        self.wait()

        self.play(FadeOut(dots))

        everything = Group(grid, grid_hd, guardian_circle, guardian_icon)

        self.play(FadeIn(grid_hd), everything.animate.scale(3).shift(LEFT * 2.5 + 2.5 * UP), run_time=2)
        self.wait()

        angle1 = -30 * DEGREES
        angle2 = -45 * DEGREES
        radius = 32 * CHUNK * grid.get_x_unit_size()
        circle_centre = guardian_icon.get_center()

        dot1_pos = circle_centre + radius * np.array([np.cos(angle1), np.sin(angle1), 0])
        dot2_pos = circle_centre + radius * np.array([np.cos(angle2), np.sin(angle2), 0])

        dot1 = Dot(dot1_pos, radius=0.05, color=BLUE)
        dot2 = Dot(dot2_pos, radius=0.05, color=BLUE)

        chord = Line(dot1_pos, dot2_pos, color=BLUE, stroke_width=5)

        chord_centre = (dot1_pos + dot2_pos) / 2
        perpendicular = Line(chord_centre, circle_centre, color=BLUE, stroke_width=5)

        chord_vector = dot2_pos - dot1_pos
        chord_angle = np.arctan2(chord_vector[1], chord_vector[0])

        right_angle = Square(
            side_length=0.2,
            color=BLUE,
            fill_opacity=0,
            stroke_width=1.5,
        ).rotate(chord_angle)

        bl_relative = 0.1 * np.array([
            np.sin(chord_angle) - np.cos(chord_angle),
            -np.sin(chord_angle) - np.cos(chord_angle),
            0
        ])

        right_angle.move_to(chord_centre + bl_relative)

        distance = np.linalg.norm(circle_centre - chord_centre)
        distance_units = distance / grid.get_x_unit_size()
        label = Text(f"{distance_units:.2f} blocks", color=BLUE, font_size=24)
        label.move_to((chord_centre + circle_centre) / 2 + 1 * UP + 0.5 * RIGHT)

        end_dot = Dot(circle_centre, radius=0.1, color=BLUE)

        self.play(FadeIn(dot1), FadeIn(dot2))
        self.wait()
        self.play(Create(chord))
        self.wait()
        self.play(Create(perpendicular), Create(right_angle))
        self.play(FadeIn(end_dot))
        self.wait()
        self.play(Write(label))
        self.wait()

if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py {name.capitalize()}")
