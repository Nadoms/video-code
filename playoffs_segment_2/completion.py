from math import isnan
from manim import *
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
Y_MIN = 300
Y_MAX = 1800
Y_STEP = 300
X_MIN = 0
X_MAX = 771
X_STEP = X_MAX * 4
DAY = 60 * 60 * 24


def compute_moving_average(data_points, window_size=5, step=1):
    data_points.sort(key=lambda x: x[0])
    start = int(data_points[0][0] + window_size / 2)
    end = int(data_points[-1][0] - window_size / 2)
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


def format_time(raw_time):
    time = str(timedelta(seconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]
    return time


class Plot(Scene):

    def construct(self):
        # Data
        data_file = DATA_DIR / "completions.csv"
        data_points = pd.read_csv(data_file).values.tolist()
        first_match = data_points[0][0]
        data_points = [
            (
                round((data[0] - first_match) / 60 / 60 / 24, 3),
                data[1],
                data[2],
                data[3],
                data[4]
            )
            for data in data_points[-5000:]
            if data[1] > 360000
        ]

        # Title
        title = Text("Completion Times Throughout Ranked History", font_size=24)
        title.move_to(ORIGIN).shift(UP * 1)

        # Axes
        plane = NumberPlane(
            x_range=[X_MIN, X_MAX, X_STEP],
            y_range=[Y_MIN, Y_MAX, Y_STEP],
            axis_config={
                "include_numbers": False,
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
                "stroke_color": DARK_GRAY,
                "stroke_width": 1,
            },
            faded_line_style={
                "stroke_color": DARKER_GRAY,
                "stroke_width": 1,
            },
            faded_line_ratio=2,
        )

        def format_date(month, year):
            date = datetime(year=year, month=month, day=1)
            days_since = round((date.timestamp() - first_match) / 60 / 60 / 24, 3)
            return date.strftime("%b '%y"), days_since

        x_labels = VGroup()
        for x in range(2, 15):
            month, days_since = format_date(x * 2 % 12 + 1, 2023 + x * 2 // 12)
            label = Tex(month).scale(0.3).next_to(
                plane.x_axis.n2p(days_since), DOWN, buff=0.2
            )
            x_labels.add(label)
        y_labels = VGroup()
        for y in range(Y_MIN, Y_MAX + 1, Y_STEP):
            label = Tex(format_time(y)).scale(0.3).next_to(
                plane.y_axis.n2p(y), LEFT, buff=0.2
            )
            y_labels.add(label)

        # Axes labels
        labels = plane.get_axis_labels(
            Tex("Month").scale(0.4),
            Tex("Completion Time").scale(0.4)
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
            if not isnan(elo):
                colour_scale = min(max((elo - 600), 0) / 1500, 1)
            else:
                colour_scale = 0
            alpha_scale = max(min(1, ((1800 - time) / 300)), 0)
            colour = ManimColor.from_rgb((
                int((1 - colour_scale) * 255),
                100,
                int(colour_scale * 255)
            ), 1)

            dot = Dot(plane.c2p(date, time), color=colour, radius=0.007).set_opacity(alpha_scale)
            if i % 1000 == 0:
                print(i)
            dots.add(dot)
            for max_elo in rank_dots:
                if not isnan(elo) and elo < max_elo:
                    rank_dots[max_elo].add(dot)
                    break
            if bastion in bastion_dots:
                bastion_dots[bastion].add(dot)
            if ow in ow_dots:
                ow_dots[ow].add(dot)

        # Lineage
        rank_lines = {
            900: None,
            1200: None,
            1500: None,
            2000: None,
            3000: None,
        }
        bastion_lines = {
            "BRIDGE": None,
            "HOUSING": None,
            "STABLES": None,
            "TREASURE": None,
        }
        ow_lines = {
            "BURIED_TREASURE": None,
            "DESERT_TEMPLE": None,
            "RUINED_PORTAL": None,
            "SHIPWRECK": None,
            "VILLAGE": None,
        }

        min_elo = 0
        for max_elo in rank_lines:
            smoothed_date, smoothed_time = compute_moving_average(
                [
                    (data[0], data[1])
                    for data in data_points
                    if not isnan(data[2]) and min_elo <= int(data[2]) < max_elo
                ]
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
                [(data[0], data[1]) for data in data_points if data[3] == bastion]
            )
            bastion_lines[bastion] = plane.plot_line_graph(
                x_values=smoothed_date,
                y_values=smoothed_time,
                stroke_width=2,
                add_vertex_dots=False,
            )
        for ow in ow_lines:
            smoothed_date, smoothed_time = compute_moving_average(
                [(data[0], data[1]) for data in data_points if data[4] == ow]
            )
            ow_lines[ow] = plane.plot_line_graph(
                x_values=smoothed_date,
                y_values=smoothed_time,
                stroke_width=2,
                add_vertex_dots=False,
            )
        smoothed_date, smoothed_time = compute_moving_average(
            [(data[0], data[1]) for data in data_points]
        )
        line = plane.plot_line_graph(
            x_values=smoothed_date,
            y_values=smoothed_time,
            stroke_width=2,
            add_vertex_dots=False,
        )

        # Animation
        self.play(Write(title), Write(plane))
        self.play(Write(labels), Write(x_labels), Write(y_labels))
        self.wait()
        self.play(FadeIn(dots), run_time=1)
        self.play(Write(line), run_time=6)
        self.wait()
        self.play(FadeOut(dots, line))
        self.wait()
        self.play(FadeIn(rank_dots[3000], rank_lines[3000]))
        self.wait()
        self.play(*[FadeIn(rank_dots[max_elo], rank_lines[max_elo]) for max_elo in rank_lines if max_elo != 3000])
        self.wait()
        self.play(*[FadeOut(rank_dots[max_elo], rank_lines[max_elo]) for max_elo in rank_lines])
        self.wait()
        self.play(*[FadeIn(bastion_dots[bastion], bastion_lines[bastion]) for bastion in bastion_lines])


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 2880,1080 -o {name}.mp4 {name}.py {name.capitalize()}")
