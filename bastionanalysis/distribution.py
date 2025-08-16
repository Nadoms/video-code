from datetime import timedelta
import json
from pathlib import Path
import re
import sys
from manim import *
import math
import pandas as pd
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from rankedutils import db

X_MIN = 1
X_MAX = 6
STEP = 1 / 12
CLASSES = int((X_MAX - X_MIN) / STEP)
BASTIONS = ["bridge", "housing", "stables", "treasure"]


class Plot(Scene):

    def construct(self):
        bastion_times = {}
        medians = {}
        median_classes = {}
        histogram = {
            "bridge": [0] * CLASSES,
            "housing": [0] * CLASSES,
            "stables": [0] * CLASSES,
            "treasure": [0] * CLASSES,
        }
        with open(ROOT_DIR / "bastionanalysis" / "data" / "bastion_splits.json") as f:
            bastion_times = json.load(f)
            for bastion in bastion_times:
                for time in bastion_times[bastion]:
                    time = time / 60000
                    time_class = math.floor((time - X_MIN) / STEP)
                    if 0 <= time_class < CLASSES:
                        histogram[bastion][time_class] += 1
                medians[bastion] = np.median(bastion_times[bastion]) / 60000
                median_classes[bastion] = math.floor((medians[bastion] - X_MIN) / STEP)

        title_top = Text(
            "Distribution of",
            font_size=20
        ).move_to(ORIGIN).shift(UP * 3.5)

        title_bottom = Text(
            f"At 2000+ Elo",
            font_size=20
        ).move_to(ORIGIN).shift(UP * 2.5)

        charts = [
            BarChart(
                bar_names=[f"{digital_time(i * STEP + X_MIN)}" if i % (0.5 / STEP) == 0 else ""  for i in range(CLASSES)],
                values=histogram[bastion],
                y_range=[0, 75, 10],
                axis_config={"font_size": 20},
                x_axis_config={
                    "include_ticks": False,
                    "include_numbers": False
                }
            )
            for bastion in BASTIONS
        ]

        labels = charts[0].get_axis_labels(
            Tex("Time").scale(0.5),
            Tex("Frequency").scale(0.5)
        )

        self.play(Write(charts[0].axes), Write(labels), Write(title_top), Write(title_bottom))

        last_bars = VMobject()
        charts = charts + [charts[0]]
        for i, chart in enumerate(charts):
            i = i % 4
            bars = chart.bars
            median_bar = bars[median_classes[BASTIONS[i]]]
            bastion_name = BASTIONS[charts.index(chart)].capitalize()

            highroll = np.percentile(bastion_times[BASTIONS[i]], 10) / 60000
            median = medians[BASTIONS[i]]
            lowroll = np.percentile(bastion_times[BASTIONS[i]], 90) / 60000
            std = np.std(bastion_times[BASTIONS[i]]) / 60000

            highroll_txt = Text(f"Highroll: {digital_time(highroll)}\n", font_size=18)
            median_txt = Text(f"Median: {digital_time(median)}\n", font_size=18)
            lowroll_txt = Text(f"Lowroll: {digital_time(lowroll)}\n", font_size=18)
            std_txt = Text(f"Std Deviation: {std:.2f}\n", font_size=18)
            stats_text = VGroup(highroll_txt, median_txt, lowroll_txt, std_txt).arrange(DOWN, aligned_edge=RIGHT)
            stats_text.shift(RIGHT * 5 + UP * 2.5)

            title_middle = Text(
                f"{bastion_name} Bastion Splits",
                font_size=24
            ).move_to(ORIGIN).shift(UP * 3)
            self.play(FadeIn(bars), FadeOut(last_bars), Write(title_middle), Write(stats_text), run_time=1)
            self.play(Indicate(median_bar, 1), run_time=3)
            self.play(Unwrite(title_middle), Unwrite(stats_text), run_time=0.3)
            last_bars = bars


def digital_time(raw_time):
    time = str(timedelta(minutes=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


# Execute rendering
if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(fr"manim -qk -v WARNING -p --disable_caching -r 1920,1080 -o {name}.mp4 {name}.py Plot")
