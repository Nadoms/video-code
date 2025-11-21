import json
from math import isnan
import numpy as np
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
X_MAX = 930
X_STEP = 15
CLASSES = int((X_MAX - X_MIN) / X_STEP)
ROOT = Path(__file__).resolve().parent
PERCENTILES = [5, 20, 50, 80, 95]


class Plot(Scene):

    def construct(self):
        import os
        # Theme
        Text.set_default(font="Minecraft")

        # Data
        with open(ROOT / "data" / "comp_history.json", "r") as f:
            data = json.load(f)

        data_oi = data["v_strid"]
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
        title = Text(f"v_strid's completions", font_size=24)
        title.to_edge(UP, buff=0.7)

        # Bar chart
        chart = BarChart(
            bar_names=[f"{numb.digital_time(1000 * (i * X_STEP + X_MIN))}" if i % 4 == 0 else "" for i in range(CLASSES)],
            y_range=[0, max(histogram), 20],
            values=histogram,
            axis_config={"font_size": 20},
            bar_width=1
        )

        [name.shift(LEFT * 0.18) for name in chart.x_axis.labels]

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

        # Bin centers in seconds
        bin_centers = [((i * X_STEP + X_MIN) + X_STEP / 2) for i in range(CLASSES)]

        counts = np.array(histogram, dtype=float)

        # Gaussian smoothing kernel (in number of bins)
        sigma_bins = max(1.0, CLASSES * 0.03)
        kernel_size = int(max(3, sigma_bins * 8)) | 1  # make odd
        xs = np.linspace(-4 * sigma_bins, 4 * sigma_bins, kernel_size)
        kernel = np.exp(-0.5 * (xs / sigma_bins) ** 2)
        kernel /= kernel.sum()

        counts_smoothed = np.convolve(counts, kernel, mode="same")
        for i in range(len(counts)):
            print(counts[i], float(counts_smoothed[i]))

        # Map smoothed counts to scene coordinates using hidden_axes
        curve_points = [hidden_axes.c2p(float(xc), float(y)) for xc, y in zip(bin_centers, counts_smoothed)]
        # Create a smooth VMobject through those points
        if len(curve_points) >= 2:
            smooth_curve = VMobject()
            smooth_curve.set_points_smoothly(curve_points)
            smooth_curve.set_stroke(BLUE, width=3)
            smooth_curve.set_fill(opacity=0)
        else:
            smooth_curve = VGroup()

        self.play(Write(labels), Write(title))
        self.play(Write(chart))
        self.play(Write(lines), Write(line_labels))


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py {name.capitalize()}")
