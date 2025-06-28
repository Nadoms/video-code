import json
from math import isnan
import random
from manim import *
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta


ROOT = Path(__file__).parent


BACKGROUND_A = (79, 27, 163)
BACKGROUND_B = (36, 6, 107)
ACCENT_A = (254, 224, 94)
ACCENT_B = (221, 169, 59)
ACCENT_C = (201, 139, 29)
ACCENT_GRADIENT = color_gradient([ACCENT_A, ACCENT_B, ACCENT_C, BLACK], 100)
SPLITS = ["time_nether", "time_bastion", "time_fortress", "time_first_portal", "time_second_portal", "time_stronghold", "time_end"]


def digital_to_raw(time: str):
    split_time = time.split(":")
    raw_time = 0
    unit = 3600
    for value in split_time:
        raw_time += int(value) * unit
        unit /= 60
    return int(raw_time)


def check_valid(time: str):
    if not isinstance(time, str):
        return False
    if ":" in time:
        return True
    return False


def read_runs(data, cutoff=15):
    runs = []
    for data_point in data:
        completion = digital_to_raw(data_point["igt"])
        if completion > cutoff * 60:
            continue

        run_splits = {}
        for split in SPLITS:
            print(data_point[split])
            if not check_valid(data_point[split]):
                continue
            run_splits[split] = digital_to_raw(data_point[split])

        run_splits["igt"] = completion
        run_splits = dict(sorted(run_splits.items(), key=lambda x:x[1]))
        if not any(split in run_splits for split in SPLITS):
            continue
        runs.append(run_splits)

    return runs


class Plot(MovingCameraScene):

    def construct(self):
        # Theme
        Text.set_default(font="Minecraft")

        # Data
        data = pd.read_csv(ROOT / "100k.csv").to_dict(orient="records")
        data = [data_point for data_point in data if data_point["igt"] and data_point["igt"] != "X"]
        runs = read_runs(data)
        print(runs, len(runs))
        max_completion = max(run["igt"] for run in runs) / 60

        # Axes
        axes = Axes(
            x_range=[0, max_completion, 2],
            y_range=[0, len(runs), 1],
            axis_config={
                "include_numbers": True,
                "stroke_opacity": 1
            }
        )

        def split_chart(number, run):
            chart = VGroup()
            x = 0
            y = len(runs) - number
            last_split = 0
            for split in run:
                width = (run[split] - last_split) / 60
                print("making a rectangle for", split)
                split_rect = Rectangle(
                    height=0.05,
                    width=width,
                    stroke_width=1,
                ).move_to(axes.c2p(x, y), LEFT)
                print(x, width)
                x = run[split] / 60
                last_split = run[split]
                chart.add(split_rect)
            print(run)
            return chart

        for i, run in enumerate(runs):
            chart = split_chart(i, run)
            axes.add(chart)

        self.add(axes)

        # Animation
        self.camera : MovingCamera


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -p -o {name}.mp4 {name}.py {name.capitalize()}")
