from datetime import timedelta
import json
from pathlib import Path
import sys
from manim import *
import pandas as pd
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from rankedutils import db


def compute_moving_average(data_points, window_size=100, step=10):
    data_points.sort(key=lambda x: x[0])
    smoothed_elo = []
    smoothed_time = []

    for elo in range(1100, 2450, step):
        lower_bound = elo - window_size / 2
        upper_bound = elo + window_size / 2

        filtered_points = [point[1] for point in data_points if lower_bound <= point[0] <= upper_bound]
        average_time = np.median(filtered_points)
        smoothed_elo.append(elo)
        smoothed_time.append(average_time / 1000)

    return smoothed_elo, smoothed_time


def find_bts():
    conn, cursor = db.start()
    matches = db.query_db(
        cursor,
        items="id",
        seedType="BURIED_TREASURE",
        type=2,
        decayed=False,
    )
    iron_time = 0
    irons = 0
    data_points = []
    for match in matches:
        runs = db.query_db(
            cursor,
            table="runs",
            items="eloRate, timeline, player_uuid",
            match_id=match[0]
        )
        for run in runs:
            elo, timeline, uuid = run
            if not elo:
                continue
            for event in reversed(json.loads(timeline)):
                if event["type"] == "story.smelt_iron":
                    print(event)
                    iron_time += event["time"]
                    irons += 1
                    data_points.append((elo, event["time"]))
    avg_iron = iron_time / irons
    return avg_iron, data_points


class Plot(Scene):

    def construct(self):
        avg_iron, data_points = find_bts()
        smoothed_elo, smoothed_time = compute_moving_average(data_points)

        title = Text("Time To Find Buried Treasures Against Player Elo", font_size=28)
        title.move_to(ORIGIN).shift(UP * 6)

        watermark = Text("By Nadoms!", color=BLUE_C, font_size=16)
        watermark.move_to(ORIGIN).shift(DOWN * 6)

        plane = NumberPlane(
            x_range=[1100, 2500, 300],
            y_range=[0, 75, 15],
            x_length=11,
            y_length=10,
            tips=True,
            axis_config={
                "include_numbers": True,
                "font_size": 26,
                "include_tip": True,
                "include_ticks": False,
            },
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

        labels = plane.get_axis_labels(
            Tex("Player Elo").scale(0.6),
            Tex("Time (s)").scale(0.6)
        )

        dots = VGroup()
        for i, (elo, time) in enumerate(data_points):
            time = time / 1000
            colour_scale = (elo - 1000) / 1450
            alpha_scale = max(min(1, ((85 - time) / 30)), 0)
            colour = ManimColor.from_rgb((
                int((1 - colour_scale) * 255),
                100,
                int(colour_scale * 255)
            ), 1)
            dot = Dot(plane.c2p(elo, time), color=colour, radius=0.015).set_opacity(alpha_scale)
            if i % 1000 == 0:
                print(i)
            dots.add(dot)

        line_plot = plane.plot_line_graph(
            x_values=smoothed_elo,
            y_values=smoothed_time,
            stroke_width=2,
            add_vertex_dots=False,
        )

        print(avg_iron)
        irons = [time for _, time in data_points]
        print(max(irons))
        print(sum(irons))
        print(len(irons))
        print(np.median(irons))

        self.add(plane)
        self.add(dots)
        self.add(title, watermark, labels, line_plot)


def digital_time(raw_time):
    raw_time = int(raw_time)
    time = str(timedelta(milliseconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


# Execute rendering
if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(fr"manim -qk -v WARNING -p --disable_caching -r 1440,1440 -o {name}.png {name}.py Plot")
