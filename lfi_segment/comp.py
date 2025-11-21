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
PLAYERS = [
    "v_strid",
    "BeefSalad",
    "bing_pigs",
    "NOHACKSJUSTTIGER",
    "7rowl",
    "silverrruns",
    "hackingnoises",
    "Kxpow",
]


class Plot(Scene):

    def construct(self):
        import os
        PLAYER_OI = os.environ.get("PLAYER")
        PLAYER_INDEX = PLAYERS.index(PLAYER_OI)
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
            np.percentile(data[PLAYER_OI], percentile)
            for percentile
            in PERCENTILES
        ]

        # Title
        title = Text(f"{PLAYER_OI.lower()} completions", font_size=24)
        title.to_edge(UP, buff=0.7)

        med_secs = percentile_data[2] / 1000.0
        print(med_secs)
        subtitle = Text(f"median - {numb.digital_time(int(med_secs) * 1000)}  ({len(data[PLAYER_OI])})", font_size=18)
        subtitle.next_to(title, DOWN)

        # Axes
        max_count = max(histogram)
        axes = Axes(
            x_range=[X_MIN, X_MAX, X_STEP],
            y_range=[0, max_count * 1.1, max(1, int(max_count / 5))],
            x_length=12,
            y_length=5,
            axis_config={
                "font_size": 20,
                "include_tip": False,
            },
        )

        # Vertical grid lines at each bin edge
        grid_lines = VGroup()
        for i in range(CLASSES + 1):
            x = X_MIN + i * X_STEP
            start = axes.c2p(x, 0)
            end = axes.c2p(x, max_count * 1.05)
            g = Line(start, end, stroke_width=1, color=GRAY, stroke_opacity=0.5)
            grid_lines.add(g)

        # Axis labels: only show x-axis label; hide y-axis
        x_label = Text("Completion Time", font_size=14)
        x_label.next_to(axes, DOWN, buff=0.5)
        axes.y_axis.set_opacity(0)

        # Prepare smoothed distributions for every player
        player_smoothed = {}
        bin_centers = [((i * X_STEP + X_MIN) + X_STEP / 2) for i in range(CLASSES)]

        sigma_bins = max(1.0, CLASSES * 0.03)
        kernel_size = int(max(3, sigma_bins * 8)) | 1
        xs = np.linspace(-4 * sigma_bins, 4 * sigma_bins, kernel_size)
        kernel = np.exp(-0.5 * (xs / sigma_bins) ** 2)
        kernel /= kernel.sum()

        for p in PLAYERS:
            if p not in data:
                continue
            data_oi_p = data[p]
            hist_p = [0] * CLASSES
            for point in data_oi_p:
                secs = point / 1000
                data_class = math.floor((secs - X_MIN) / X_STEP)
                if 0 <= data_class < CLASSES:
                    hist_p[data_class] += 1
            counts = np.array(hist_p, dtype=float)
            counts_smoothed = np.convolve(counts, kernel, mode="same")
            counts_smoothed = np.clip(counts_smoothed, 0.0, None)
            player_smoothed[p] = counts_smoothed

        # Determine max across all players to scale axes
        if player_smoothed:
            global_max = max(v.max() for v in player_smoothed.values())
        else:
            global_max = max(histogram)

        # Recompute axes vertical scaling based on global_max
        axes.y_range = [0, global_max * 1.1, max(1, int(global_max / 5))]

        # Draw each player's smoothed curve with a distinct color, normalized by default
        colors = [BLUE, RED, GREEN, ORANGE, PURPLE_D, TEAL, YELLOW, GOLD]
        from itertools import cycle
        color_cycle = cycle(colors)
        curves = VGroup()
        legend_items = VGroup()
        for p, color in zip(player_smoothed.keys(), color_cycle):
            counts_smoothed = player_smoothed[p]
            # normalize so peak == global_max
            p_max = counts_smoothed.max() if len(counts_smoothed) else 0
            if p_max <= 0:
                continue
            scale_factor = global_max / p_max
            scaled_counts = counts_smoothed * scale_factor

            curve_points = [axes.c2p(float(xc), float(y)) for xc, y in zip(bin_centers, scaled_counts)]
            left_anchor = axes.c2p(X_MIN, 0)
            right_anchor = axes.c2p(X_MAX, 0)
            anchored_points = [left_anchor] + curve_points + [right_anchor]
            smooth_curve = VMobject()
            smooth_curve.set_points_smoothly(anchored_points)
            smooth_curve.set_stroke(color, width=3)
            smooth_curve.set_fill(color, opacity=0.01)
            curves.add(smooth_curve)
            # legend
            dot = Square(side_length=0.25, fill_color=color, fill_opacity=1, stroke_width=0)
            lbl = Text(p, font_size=20).scale(0.6).next_to(dot, RIGHT, buff=0.1)
            legend_items.add(VGroup(dot, lbl))

        # Add back x tick labels at every 4th bin (bar name labels)
        x_tick_labels = VGroup()
        for i in range(CLASSES):
            if i % 4 == 0:
                x = X_MIN + i * X_STEP
                txt = Text(f"{numb.digital_time(1000 * (i * X_STEP + X_MIN))}", font_size=14)
                txt.move_to(axes.c2p(x, 0) + DOWN * 0.3)
                x_tick_labels.add(txt)

        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        legend_items.to_corner(UR)

        # Median line for the selected player index
        median_line = None
        if 0 <= PLAYER_INDEX < len(PLAYERS):
            sel = PLAYERS[PLAYER_INDEX]
            if sel in data and len(data[sel]) > 0:
                x_med = axes.c2p(med_secs, 0)[0]
                y0 = axes.c2p(med_secs, 0)[1]
                y1 = axes.c2p(med_secs, global_max)[1] + 0.5
                median_line = DashedLine(start=[x_med, y0, 0], end=[x_med, y1, 0], dash_length=0.08, color=YELLOW_B)

        items = [axes, grid_lines, x_label, x_tick_labels, curves[PLAYER_INDEX], legend_items, title, subtitle]
        if median_line is not None:
            # insert median_line just before the legend so it appears above grid but below legend
            items.insert(-2, median_line)

        self.add(*items)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    for player in PLAYERS:
        os.system(rf"PLAYER={player} manim -qp -o comp_{player[:3]} {name}.py {name.capitalize()}")
