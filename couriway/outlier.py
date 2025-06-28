import json
from math import isnan
import random
from manim import *
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta


ROOT = Path(__file__).parent


X_MIN = 600
X_MAX = 3600
X_STEP = 5
BACKGROUND_A = (79, 27, 163)
BACKGROUND_B = (36, 6, 107)
ACCENT_A = (254, 224, 94)
ACCENT_B = (221, 169, 59)
ACCENT_C = (201, 139, 29)
ACCENT_GRADIENT = color_gradient([ACCENT_A, ACCENT_B, ACCENT_C, BLACK], 100)


def digital_to_raw(time: str):
    split_time = time.split(":")
    raw_time = 0
    unit = 3600
    for value in split_time:
        raw_time += int(value) * unit
        unit /= 60
    return int(raw_time)


class Plot(MovingCameraScene):

    def construct(self):
        # Theme
        Text.set_default(font="Minecraft")

        # Data
        data = pd.read_csv(ROOT / "100k.csv").to_dict(orient="records")
        completions = [digital_to_raw(data_point["igt"]) for data_point in data if data_point["igt"] and data_point["igt"] != "X"]
        pb_run = completions[30]
        jeb_run = completions[999]
        completions.sort()

        # Axes
        axes = Axes(
            x_range=[X_MIN, X_MAX, X_STEP],
            y_range=[-40, 40, 1],
            axis_config={
                "include_numbers": False,
                "include_tip": False,
                "stroke_opacity": 0
            }
        )

        dots = VGroup()
        completions_cumulative = []
        for i, completion in enumerate(completions):
            if completion == pb_run:
                continue
            close_runs = i - np.searchsorted(completions_cumulative, completion - 10)
            y_height = random.randrange(-close_runs, close_runs + 1) / 2 + (0.5 - random.random()) / 4
            colour_scale = min(int(completion / 36), 99)
            colour = ACCENT_GRADIENT[colour_scale]
            dot = Dot(axes.c2p(completion, y_height), color=colour, radius=0.01)
            dots.add(dot)
            completions_cumulative.append(completion)

        pb_dot = Dot(axes.c2p(pb_run, 0), color=GREEN, radius=0.01)
        pb_text = Text("XX:XX").scale(0.01).next_to(pb_dot, direction=UP, buff=0.005)
        jeb_dot = Dot(axes.c2p(jeb_run, 0), color=GREEN, radius=0.01)
        jeb_text = Text("23:46").scale(0.01).next_to(jeb_dot, direction=UP, buff=0.005)

        # Animation
        self.camera : MovingCamera
        self.add(pb_dot, jeb_dot, pb_text, jeb_text)
        self.camera.frame.save_state()
        self.camera.auto_zoom(jeb_dot, animate=False)
        self.wait()
        self.play(self.camera.frame.animate(rate_func=smooth).scale(400).move_to(axes), Write(dots), run_time=10)
        self.wait()
        self.play(self.camera.frame.animate(rate_func=smooth).scale(1 / 100).move_to(pb_dot), run_time=10)
        self.wait()


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -p -o {name}.mp4 {name}.py {name.capitalize()}")
