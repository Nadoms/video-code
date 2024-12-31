from datetime import timedelta
import json
from pathlib import Path
import re
from manim import *
import math
import pandas as pd
import os

BASTIONS = ["bridge", "housing", "stables", "treasure"]
TIME_PATTERN = r"^.*\s(\d:\d\d:\d\d)"


class Distribution(Scene):

    def construct(self):
        bastion_times = {
            "bridge": [],
            "housing": [],
            "stables": [],
            "treasure": [],
        }
        histogram = {
            "bridge": [0] * 150,
            "housing": [0] * 150,
            "stables": [0] * 150,
            "treasure": [0] * 150,
        }
        for bastion in BASTIONS:
            times = []
            with open(Path(__file__).parent / "data" / bastion / "0.txt") as b:
                while True:
                    line = b.readline()
                    if not line:
                        break
                    match = re.search(TIME_PATTERN, line)
                    if match:
                        time = get_raw_time(match.group(1)) / 1000
                        bastion_times[bastion].append(time)
                        times_class = min(math.floor(time / 5), 150 - 1)
                        histogram[bastion][times_class] += 0.2
            with open(Path(__file__).parent / "data" / bastion / "1.txt") as b:
                while True:
                    line = b.readline()
                    if not line:
                        break
                    match = re.search(TIME_PATTERN, line)
                    if match:
                        time = get_raw_time(match.group(1)) / 1000
                        bastion_times[bastion].append(time)
                        times_class = min(math.floor(time / 5), 150 - 1)
                        histogram[bastion][times_class] += 0.2
            bastion_times[bastion] = sorted(bastion_times[bastion])

        title = Text("Distribution of Bridge Bastion Splits Below 900 Elo", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        charts = [
            BarChart(
                bar_names=[f"{digital_time(i * 5000)}" if i % 12 == 0 else "" for i in range(150)],
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
            Tex("Frequency Density (/min)").scale(0.5)
        )

        self.play(Write(title))
        self.play(Write(charts[0]))
        self.play(Write(labels))

        for chart in charts:
            bars = chart.bars
            bastion_name = BASTIONS[charts.index(chart)].capitalize()
            if chart != charts[0]:
                title = Text(
                    f"Distribution of {bastion_name} Bastion Splits Below 900 Elo",
                    font_size=24
                ).move_to(ORIGIN).shift(UP * 3)
                self.play(Write(bars), Write(title))
                self.wait()
            self.play(Unwrite(bars), Unwrite(title))


def get_raw_time(time):
    raw_time = 0
    time = list(reversed(time.split(":")))

    for i, value in enumerate(time):
        raw_time += int(value) * (60 ** i)

    return raw_time * 1000


def digital_time(raw_time):
    raw_time = int(raw_time)
    time = str(timedelta(milliseconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


# Execute rendering
if __name__ == "__main__":
    os.system(r"manim -qk -v WARNING -p --disable_caching -r 1280,720 -o distribution_neth.mp4 .\distribution_neth.py Distribution")