import json
from math import isnan
import math
import random
from manim import *
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from rankedutils import numb, word

ROOT = Path(__file__).parent
player = None
season = None

X_MIN = 360
X_MAX = 840
X_STEP = 20
CLASSES = int((X_MAX - X_MIN) / X_STEP)
ROOT = Path(__file__).resolve().parent
PERCENTILES = [5, 20, 50, 80, 95]


class Plot(Scene):

    def construct(self):
        import os
        # Theme
        Text.set_default(font="Minecraft")

        player = os.environ.get("PLAYER")
        season = os.environ.get("SEASON")

        # Data
        data_file = ROOT / "data.json"
        with open(data_file, "r") as f:
            data = json.load(f)

        data_oi = data[player][str(season)]["comp"]
        histogram = [0] * CLASSES
        for point in data_oi:
            secs = point / 1000
            data_class = math.floor((secs - X_MIN) / X_STEP)
            if 0 <= data_class < CLASSES:
                histogram[data_class] += 1

        percentile_data = [
            np.percentile(data_oi, percentile)
            for percentile
            in PERCENTILES
        ]

        # Title
        title = Text(f"{player.capitalize()}'s Completions - S{season}", font_size=24)
        title.to_edge(UP, buff=0.7)

        # Bar chart
        chart = BarChart(
            bar_names=[f"{numb.digital_time(1000 * (i * X_STEP + X_MIN))}" if i % 3 == 0 else "" for i in range(CLASSES)],
            y_range=[0, max(histogram), 5],
            values=histogram,
            axis_config={"font_size": 16},
            x_axis_config={
            },
            bar_width=1
        )

        [name.shift(LEFT * 0.25) for name in chart.x_axis.labels]

        # Axes labels
        labels = chart.get_axis_labels(
            Tex("Completion Time").scale(0.5),
            Tex("Count").scale(0.5)
        )

        # Percentile lines
        hidden_axes = Axes(
            x_range=[X_MIN, X_MAX, X_STEP],
            y_range=[0, max(histogram) // 5 * 5 + 5, 5],
            x_length=chart.x_axis.length,
            y_length=chart.y_axis.length,
            axis_config={
                "include_tip": False
            },
        )

        lines = VGroup()
        line_labels = VGroup()
        for perc, percentile in zip(PERCENTILES, percentile_data):
            secs = percentile / 1000
            x_pixel = hidden_axes.c2p(secs, 0)[0]
            y0 = hidden_axes.c2p(secs, 0)[1]
            y1 = hidden_axes.c2p(secs, max(histogram))[1]
            line = Line(
                start=[x_pixel, y0, 0],
                end=[x_pixel, y1, 0],
                color=YELLOW,
                stroke_width=3,
                z_index=2
            )
            lines.add(line)
            label_text_1 = f"{perc}%"
            label_text_2 = numb.digital_time(int(percentile))
            label_2 = Text(label_text_2, font_size=14).next_to(line, UP, buff=0.1)
            label_1 = Text(label_text_1, font_size=18).next_to(label_2, UP, buff=0.1)
            line_labels.add(label_1, label_2)

        self.add(chart, labels, lines, line_labels, title)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    for p in ["doogile", "Lowk3y_"]:
        for s in range(1, 10):
            os.system(rf"PLAYER={p} SEASON={s} manim -qp -o {p}{s} {name}.py {name.capitalize()}")
