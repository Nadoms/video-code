from math import isnan
from manim import *
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
X_MIN = 0
X_MAX = 90
X_STEP = 5
Y_MIN = 0
Y_MAX = 100
Y_STEP = Y_MAX * 4
CLASSES = int((X_MAX - X_MIN) / X_STEP)


class Plot(Scene):

    def construct(self):
        # Data
        histogram = [0] * CLASSES
        histogram_po = [0] * CLASSES
        po_data_points = {
            "BURIED_TREASURE": [],
            "DESER_TEMPLE": [],
            "RUINED_PORTAL": [],
            "SHIPWRECK": [],
            "VILLAGE": [],
        }
        data_file = DATA_DIR / "disparity.csv"
        data_points = pd.read_csv(data_file).values.tolist()
        for elo, _, o_type, overworld, _, _, _, _, _ in data_points:
            overworld = overworld / 1000
            if isnan(overworld):
                continue
            overworld_class = int((overworld - X_MIN) // X_STEP)
            if 0 <= overworld_class < CLASSES:
                histogram[overworld_class] += 1
                if elo == 3000:
                    histogram_po[overworld_class]
                    po_data_points[o_type].append(overworld)


        po_box_plot = {
            o_type: [
                min(po_data_points[o_type]),
                np.percentile(po_data_points[o_type], 25),
                np.median(po_data_points[o_type]),
                np.percentile(po_data_points[o_type], 75),
                max(po_data_points[o_type]),
            ] if po_data_points[o_type] else None
            for o_type in po_data_points
        }

        # Title
        title = Text("Nether Enter Disparity", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        # Chart
        chart = BarChart(
            bar_names=[f"{digital_time(i * X_STEP + X_MIN)}" if i % (10 / X_STEP) == 0 else "" for i in range(CLASSES)],
            values=histogram,
            y_range=[0, 200, 25],
            axis_config={"font_size": 20},
            x_axis_config={
                "include_ticks": False,
                "include_numbers": False
            }
        )
        chart_po = BarChart(
            bar_names=[f"{digital_time(i * X_STEP + X_MIN)}" if i % (10 / X_STEP) == 0 else "" for i in range(CLASSES)],
            values=histogram_po,
            y_range=[0, 30, 5],
            axis_config={"font_size": 20},
            x_axis_config={
                "include_ticks": False,
                "include_numbers": False
            }
        )

        # Axes labels
        labels = chart.get_axis_labels(
            Tex("Pace Difference (s)").scale(0.5),
            Tex("Frequency").scale(0.5)
        )

        # Animation
        self.play(Write(chart), Write(title))
        self.play(Write(labels))

        self.play(Unwrite(chart))
        self.play(Write(chart_po))


def digital_time(raw_time):
    time = str(timedelta(seconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 1920,1080 -o {name}.mp4 {name}.py {name.capitalize()}")
