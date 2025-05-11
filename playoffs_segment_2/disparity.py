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
X_MAX = 121
X_STEP = 1
Y_MIN = 0
Y_MAX = 8000
Y_STEP = 2000
PO_X_MIN = 0
PO_X_MAX = 61
PO_X_STEP = 1
PO_Y_MIN = 0
PO_Y_MAX = 20
PO_Y_STEP = 5
CLASSES = int((X_MAX - X_MIN) / X_STEP)
PO_CLASSES = int((PO_X_MAX - PO_X_MIN) / PO_X_STEP)


class Plot(Scene):

    def construct(self):
        # Data
        histogram = [0] * CLASSES
        histogram_po = [0] * CLASSES
        ow_data_points = {
            "BURIED_TREASURE": [],
            "DESERT_TEMPLE": [],
            "RUINED_PORTAL": [],
            "SHIPWRECK": [],
            "VILLAGE": [],
        }
        data_file = DATA_DIR / "disparity.csv"
        below_20 = 0
        below_20_po = 0
        total = 0
        total_po = 0
        data_points = pd.read_csv(data_file).values.tolist()
        for elo, _, o_type, overworld, _, _, _, _, _, _ in data_points:
            overworld = overworld / 1000
            if isnan(overworld):
                continue
            total += 1
            if elo == 3000:
                total_po += 1
            if overworld < 20:
                below_20 += 1
                if elo == 3000:
                    below_20_po += 1
            overworld_class = int((overworld - X_MIN) // X_STEP)
            if 0 <= overworld_class < CLASSES:
                histogram[overworld_class] += 1
                if elo == 3000:
                    histogram_po[overworld_class] += 1
                else:
                    ow_data_points[o_type].append(overworld)

        ow_box_plot = {
            o_type: [
                min(ow_data_points[o_type]),
                np.percentile(ow_data_points[o_type], 25),
                np.median(ow_data_points[o_type]),
                np.percentile(ow_data_points[o_type], 75),
                max(ow_data_points[o_type]),
            ] if ow_data_points[o_type] else None
            for o_type in ow_data_points
        }

        # Title
        Text.set_default(font="Minecraft")
        title = Text("Nether Enter Disparity", font_size=28)
        title.move_to(ORIGIN).shift(UP * 3)
        # Subtitles
        general_title = Text("Across all S7 (and some S8) games", font_size=18)
        general_title.next_to(title, DOWN, buff=0.1)
        po_title = Text("In all playoffs matches", font_size=18)
        po_title.next_to(title, DOWN, buff=0.1)

        # Chart
        chart = BarChart(
            bar_names=[f"{digital_time(i * X_STEP + X_MIN)}" if i % (10 / X_STEP) == 0 else "" for i in range(CLASSES)],
            values=histogram,
            y_range=[Y_MIN, Y_MAX, Y_STEP],
            axis_config={"font_size": 20},
            x_axis_config={
                "include_ticks": False,
                "include_numbers": False
            }
        )
        chart_po_old = BarChart(
            bar_names=[f"{digital_time(i * X_STEP + X_MIN)}" if i % (10 / X_STEP) == 0 else "" for i in range(CLASSES)],
            values=histogram_po,
            y_range=[PO_Y_MIN, PO_Y_MAX, PO_Y_STEP],
            axis_config={"font_size": 20},
            x_axis_config={
                "include_ticks": False,
                "include_numbers": False
            }
        )
        chart_po = BarChart(
            bar_names=[f"{digital_time(i * PO_X_STEP + PO_X_MIN)}" if i % (10 / PO_X_STEP) == 0 else "" for i in range(PO_CLASSES)],
            values=histogram_po[:PO_CLASSES],
            y_range=[PO_Y_MIN, PO_Y_MAX, PO_Y_STEP],
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
        labels[0].shift(DOWN)
        text_1 = Text(f"{(below_20 / total * 100):.1f}% < 20s", font_size=28).move_to(ORIGIN).shift(UP + RIGHT * 2)
        text_2 = Text(f"{(below_20_po / total_po * 100):.1f}% < 20s", font_size=28).move_to(ORIGIN).shift(UP + RIGHT * 2)

        # Animation
        self.play(Write(chart.axes), Write(title), Write(general_title))
        self.play(Write(labels))
        self.play(Write(chart.bars), run_time=4)
        self.play(Write(text_1), Indicate(chart.bars[:20], scale_factor=1, run_time=3))
        self.wait()
        self.play(Unwrite(general_title))
        self.play(FadeOut(chart.bars, chart.y_axis), Unwrite(text_1), Write(po_title), FadeIn(chart_po_old.bars, chart_po_old.y_axis))
        self.play(Write(text_2), Indicate(chart_po_old.bars[:20], scale_factor=1, run_time=3))
        self.wait()
        # self.play(Unwrite(chart_po_old, chart.x_axis), run_time=0.5)
        # self.play(Write(chart_po), run_time=0.5)
        # self.wait()


def digital_time(raw_time):
    time = str(timedelta(seconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 2560,1440 -o {name}.mp4 {name}.py {name.capitalize()}")
