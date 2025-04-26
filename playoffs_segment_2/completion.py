from io import BytesIO
import json
from manim import *
import os
from pathlib import Path
from PIL import Image
import pandas as pd
import requests
from datetime import datetime, timedelta


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
Y_MIN = 0
Y_MAX = 1800
Y_STEP = 300
X_MIN = 0
X_MAX = 730
X_STEP = 30.4
DAY = 60 * 60 * 24


def compute_moving_average(data_points, start, end, window_size=100, step=10):
    data_points.sort(key=lambda x: x[0])
    smoothed_date = []
    smoothed_time = []

    for date in range(start, end, step):
        lower_bound = date - window_size / 2
        upper_bound = date + window_size / 2

        filtered_points = [point[1] for point in data_points if lower_bound <= point[0] <= upper_bound]
        average_time = np.median(filtered_points)
        smoothed_date.append(date)
        smoothed_time.append(average_time / 1000)

    return smoothed_date, smoothed_time


class Plot(Scene):

    def construct(self):
        # Data
        data_file = DATA_DIR / "history.csv"
        data_points = pd.read_csv(data_file)
        first_match = round(min(int(match[0]) for match in data_points) / 60 / 60 / 24, 3)
        now = round(datetime.now().timestamp() / 60 / 60 / 24, 3)

        # Axes
        plane = NumberPlane(
            x_range=[X_MIN, X_MAX, X_STEP],
            y_range=[Y_MIN, Y_MAX, Y_STEP],
            axis_config={
                "include_numbers": True,
                "font_size": 20,
                "include_tip": False,
            },
            x_length=11,
            y_length=3.5,
            y_axis_config={
                "label_direction": LEFT,
            },
            x_axis_config={
                "label_direction": DOWN,
            },
            background_line_style={
                "stroke_color": LIGHT_GRAY,
                "stroke_width": 1,
            },
            faded_line_style={
                "stroke_color": DARK_GRAY,
                "stroke_width": 1,
            },
            faded_line_ratio=3,
        )

        # Axes labels
        labels = plane.get_axis_labels(
            Tex("Date").scale(0.5),
            Tex("Completion Time").scale(0.5)
        )

        # Dottage
        dots = VGroup()
        rank_dots = {
            600: VGroup(),
            900: VGroup(),
            1200: VGroup(),
            1500: VGroup(),
            2000: VGroup(),
            3000: VGroup(),
        }
        bastion_dots = {
            "BRIDGE": VGroup(),
            "HOUSING": VGroup(),
            "STABLES": VGroup(),
            "TREASURE": VGroup(),
        }
        ow_dots = {
            "BURIED_TREASURE": VGroup(),
            "DESERT_TEMPLE": VGroup(),
            "RUINED_PORTAL": VGroup(),
            "SHIPWRECK": VGroup(),
            "VILLAGE": VGroup(),
        }
        for i, (date, time, elo, bastion, ow) in enumerate(data_points):
            time = time / 1000
            colour_scale = max((elo - 600), 0) / 2550
            alpha_scale = max(min(1, ((1800 - time) / 300)), 0)
            colour = ManimColor.from_rgb((
                int((1 - colour_scale) * 255),
                100,
                int(colour_scale * 255)
            ), 1)
            day = round(first_match + date, 3)

            dot = Dot(plane.c2p(day, time), color=colour, radius=0.015).set_opacity(alpha_scale)
            if i % 1000 == 0:
                print(i)
            dots.add(dot)
            for max_elo in rank_dots:
                if elo < max_elo:
                    rank_dots[max_elo].add(dot)
            bastion_dots[bastion].add(dot)
            ow_dots[ow].add(dot)

        # Lineage
        rank_lines = VDict(mapping_or_iterable={
            600: None,
            900: None,
            1200: None,
            1500: None,
            2000: None,
            3000: None,
        })
        bastion_lines = VDict(mapping_or_iterable={
            "BRIDGE": None,
            "HOUSING": None,
            "STABLES": None,
            "TREASURE": None,
        })
        ow_lines = VDict(mapping_or_iterable={
            "BURIED_TREASURE": None,
            "DESERT_TEMPLE": None,
            "RUINED_PORTAL": None,
            "SHIPWRECK": None,
            "VILLAGE": None,
        })

        min_elo = 0
        for max_elo in rank_lines:
            smoothed_date, smoothed_time = compute_moving_average(
                [(int(data[0]), int(data[1])) for data in data_points if min_elo <= int(data[2]) < max_elo]
            )
            min_elo = max_elo
            rank_lines[max_elo] = plane.plot_line_graph(
                x_values=smoothed_date,
                y_values=smoothed_time,
                stroke_width=2,
                add_vertex_dots=False,
            )
        for bastion in bastion_lines:
            smoothed_date, smoothed_time = compute_moving_average(
                [(int(data[0]), int(data[1])) for data in data_points if data[3] == bastion]
            )
            bastion_lines[bastion] = plane.plot_line_graph(
                x_values=smoothed_date,
                y_values=smoothed_time,
                stroke_width=2,
                add_vertex_dots=False,
            )
        for ow in ow_lines:
            smoothed_date, smoothed_time = compute_moving_average(
                [(int(data[0]), int(data[1])) for data in data_points if data[3] == ow]
            )
            ow_lines[ow] = plane.plot_line_graph(
                x_values=smoothed_date,
                y_values=smoothed_time,
                stroke_width=2,
                add_vertex_dots=False,
            )
        smoothed_date, smoothed_time = compute_moving_average(
            [(int(data[0]), int(data[1])) for data in data_points]
        )
        line = plane.plot_line_graph(
            x_values=smoothed_date,
            y_values=smoothed_time,
            stroke_width=2,
            add_vertex_dots=False,
        )

        # Animation
        self.play(Write(plane), Write(labels))
        self.play(Write(dots))
        self.play(Write(line), run_time=6)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 2880,1080 -o {name}.mp4 {name}.py {name.capitalize()}")
