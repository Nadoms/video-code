from io import BytesIO
import json
from manim import *
import os
from pathlib import Path
from PIL import Image
import pandas as pd
import requests


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
Y_MIN = 1000
Y_MAX = 2500
Y_STEP = 200
X_MIN = 0
X_MAX = 122
X_STEP = 10
COLOURS = [
    BLUE,
    RED,
    GREEN,
    PURPLE,
    ORANGE,
    PINK,
    YELLOW,
    TEAL,
    LIGHT_BROWN,
    LIGHT_PINK,
    LIGHT_GREY,
    DARK_BROWN,
    DARK_BLUE,
    DARK_GREY,
    GOLD,
    MAROON,
]

class Plot(Scene):

    def construct(self):
        # Data
        data_file = DATA_DIR / "history.csv"
        data = pd.read_csv(data_file)
        players = data.columns[1:]

        # Axes
        axes = Axes(
            x_range = [X_MIN, X_MAX, X_STEP],
            y_range=[Y_MIN, Y_MAX, Y_STEP],
            axis_config={
                "include_numbers": True,
                "font_size": 20,
                "include_tip": False,
            },
            x_length=11,
            y_length=3.5,
        )

        # Axes labels
        labels = axes.get_axis_labels(
            Tex("Time (Days)").scale(0.5),
            Tex("Elo").scale(0.5)
        )

        # Horizontal grid lines
        lines = VGroup()
        for y in range(Y_MIN, Y_MAX, Y_STEP):
            line = Line(
                start=axes.c2p(0, y),
                end=axes.c2p(X_MAX, y),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            lines.add(line)

        # Line plot
        line_plots = VGroup()
        for i, player in enumerate(players):
            valid_data = data[player].dropna()
            x_values = valid_data.index.tolist()
            y_values = valid_data.values.tolist()
            for j in range(len(y_values)):
                if y_values[j] != -1:
                    for k in range(j):
                        x_values[k] = x_values[j]
                        y_values[k] = valid_data[j]
                    break

            line_plot = axes.plot_line_graph(
                x_values=x_values,
                y_values=y_values,
                line_color=COLOURS[i],
                stroke_width=2,
                add_vertex_dots=False,
            )
            line_plot.set(clip=axes)
            line_plots.add(line_plot)

        # Player icons
        # player_icon = ImageMobject(ASSETS_DIR / f"{player}.png")
        # player_icon.scale(0.4).next_to(bar, DOWN)
        # player_icons.add(player_icon)

        # Animation
        self.play(Write(axes))
        self.play(Write(labels), Write(lines))
        self.play(*[Write(line_plot) for line_plot in line_plots], run_time=25)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 2880,1080 -o {name}.mp4 {name}.py {name.capitalize()}")
