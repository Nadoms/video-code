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
TIME_GRADIENT = color_gradient([BLUE_B, PURPLE_C, RED_B], 42)
SPLITS = ["time_nether", "time_bastion", "time_fortress", "time_first_portal", "time_second_portal", "time_stronghold", "time_end"]
MAJOR_SPLITS = ["OVERWORLD", "NETHER", "POST_BLIND", "END"]
COLOURS = {
    "time_ow": ManimColor.from_rgb((100, 196, 36)),
    "time_nether": ManimColor.from_rgb((114, 50, 50)),
    "time_bastion": ManimColor.from_rgb((59, 57, 70)),
    "time_fortress": ManimColor.from_rgb((60, 28, 35)),
    "time_first_portal": ManimColor.from_rgb((208, 106, 249)),
    "time_second_portal": ManimColor.from_rgb((112, 24, 194)),
    "time_stronghold": ManimColor.from_rgb((139, 137, 140)),
    "time_end": ManimColor.from_rgb((204, 198, 138)),
}


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
    runs = {}
    for data_point in reversed(data):
        run_no = int(data_point["run_id"].replace(",", ""))
        completion = digital_to_raw(data_point["igt"])
        if completion >= cutoff * 60:
            continue

        run_splits = {}
        for split in SPLITS:
            if not check_valid(data_point[split]):
                continue
            run_splits[split] = digital_to_raw(data_point[split])

        run_splits["igt"] = completion
        run_splits = dict(sorted(run_splits.items(), key=lambda x:x[1]))
        if not any(split in run_splits for split in SPLITS):
            continue
        runs[run_no] = run_splits

    major_split_runs = {}
    for run_no, run in runs.items():
        major_split_runs[run_no] = {}
        for major_split in MAJOR_SPLITS:
            if major_split == "OVERWORLD":
                major_split_runs[run_no][major_split] = run["time_nether"]
            elif major_split == "NETHER":
                major_split_runs[run_no][major_split] = run["time_first_portal"] - run["time_nether"]
            elif major_split == "POST_BLIND":
                major_split_runs[run_no][major_split] = run["time_end"] - run["time_first_portal"]
            elif major_split == "END":
                major_split_runs[run_no][major_split] = run["igt"] - run["time_end"]

    return runs, major_split_runs


def find_orderings(runs):
    orderings = {}
    run_to_index = {id(run): i for i, run in enumerate(runs)}
    for major_split in MAJOR_SPLITS:
        if major_split == "OVERWORLD":
            ordered_runs = sorted(runs, key=lambda x: x["time_nether"])
        elif major_split == "NETHER":
            ordered_runs = sorted(runs, key=lambda x: x["time_first_portal"] - x["time_nether"])
        elif major_split == "POST_BLIND":
            ordered_runs = sorted(runs, key=lambda x: x["time_end"] - x["time_first_portal"])
        elif major_split == "END":
            ordered_runs = sorted(runs, key=lambda x: x["igt"] - x["time_end"])
        ordering = [run_to_index[id(run)] for run in ordered_runs]
        orderings[major_split] = ordering
    return orderings


class Plot(MovingCameraScene):

    def construct(self):
        # Theme
        Text.set_default(font="Minecraft")

        # Titles
        title = Text("Sub 15s represented\nin their splits", font_size=18).to_corner(UL, buff=0.3)
        subtitles = {
            "OVERWORLD": Text("Sorted by overworld\nsplit duration", font_size=16).next_to(title, DOWN, buff=0.1, aligned_edge=LEFT),
            "NETHER": Text("Sorted by nether\nsplit duration", font_size=16).next_to(title, DOWN, buff=0.1, aligned_edge=LEFT),
            "POST_BLIND": Text("Sorted by finding\nend portal duration", font_size=16).next_to(title, DOWN, buff=0.1, aligned_edge=LEFT),
            "END": Text("Sorted by endfight\nduration", font_size=16).next_to(title, DOWN, buff=0.1, aligned_edge=LEFT),
        }

        # Data
        data = pd.read_csv(ROOT / "100k.csv").to_dict(orient="records")
        data = [data_point for data_point in data if data_point["igt"] and data_point["igt"] != "X"]
        runs, major_split_runs = read_runs(data)
        orderings = find_orderings(list(runs.values()))
        max_completion = max(run["igt"] for run in runs.values())

        # Axes
        axes = Axes(
            x_range=[0, max_completion, 120],
            y_range=[0, len(runs), 1],
            x_length=5,
            y_length=7,
        )

        # Vertical grid and labels
        lines = VGroup()
        x_labels = VGroup()
        for x in range(0, max_completion+60, 60):
            line = Line(
                axes.c2p(x, -1),
                axes.c2p(x, len(runs)),
                color=WHITE,
                stroke_opacity=0.15,
                stroke_width=2,
            )
            label_down = Text(str(int(x / 60)), font_size=10).next_to(line, DOWN, buff=0)
            label_up = Text(str(int(x / 60)), font_size=10).next_to(line, UP, buff=0)
            lines.add(line)
            x_labels.add(label_down)
            x_labels.add(label_up)

        # Coords
        ys = list(range(len(runs)-1, -1, -1))
        left_coords = [axes.c2p(0, y) for y in ys]
        right_coords = [axes.c2p(900, y) for y in ys]

        # Charts
        charts = VGroup()
        chart_labels = VGroup()
        chart_times = {
            "OVERWORLD": VGroup(),
            "NETHER": VGroup(),
            "POST_BLIND": VGroup(),
            "END": VGroup(),
        }

        def split_times(number, run):
            for major_split in MAJOR_SPLITS:
                if major_split == "OVERWORLD":
                    time = run["time_nether"]
                elif major_split == "NETHER":
                    time = run["time_first_portal"] - run["time_nether"]
                elif major_split == "POST_BLIND":
                    time = run["time_end"] - run["time_first_portal"]
                elif major_split == "END":
                    time = run["igt"] - run["time_end"]
                m, s = divmod(time, 60)
                time_str = f"{m}:{s:02d}"
                time_label = Text(
                    time_str,
                    font_size=8,
                    color=TIME_GRADIENT[orderings[major_split].index(number)]
                ).move_to(right_coords[orderings[major_split].index(number)], LEFT).shift(RIGHT * 0.1)
                chart_times[major_split].add(time_label)

        def split_chart(number, run, run_no):
            chart = VGroup()
            x = 0
            last_split = "time_ow"
            last_split_time = 0
            for split in run:
                width = (run[split] - last_split_time)
                start = axes.c2p(x, ys[number])
                end = axes.c2p(x + width, ys[number])
                scene_width = end[0] - start[0]

                split_rect = Rectangle(
                    height=0.1,
                    width=scene_width,
                    stroke_width=1,
                    fill_color=COLOURS[last_split],
                    fill_opacity=0.8,
                ).move_to(start, LEFT)

                x = run[split]
                last_split = split
                last_split_time = run[split]
                chart.add(split_rect)
            run_label = Text(f"#{run_no}", font_size=8).move_to(axes.c2p(0, ys[number]), RIGHT).shift(LEFT * 0.1)
            run_label = Text(f"#{run_no}", font_size=8).move_to(axes.c2p(0, ys[number]), RIGHT).shift(LEFT * 0.1)
            chart_labels.add(run_label)
            return chart

        for i, run_no in enumerate(runs):
            split_times(i, runs[run_no])
            chart = split_chart(i, runs[run_no], run_no)
            charts.add(chart)

        # Animation
        self.camera : MovingCamera
        self.play(Write(lines), Write(x_labels), Write(chart_labels), Write(title))
        self.play(Write(charts), run_time=5)
        self.camera.frame.save_state()
        self.wait()
        self.play(self.camera.auto_zoom(charts[6], margin=3), run_time=2)
        self.play(self.camera.frame.animate().shift(DOWN * 5), run_time=10)
        self.wait()
        self.play(Restore(self.camera.frame))
        self.wait()

        last_major_split = ""
        for major_split in orderings:
            animations = []
            for i, chart in enumerate(charts):
                animations.append(chart_labels[i].animate.move_to(left_coords[orderings[major_split].index(i)], RIGHT).shift(LEFT * 0.1))
                animations.append(chart.animate.move_to(left_coords[orderings[major_split].index(i)], LEFT))
            if major_split == "OVERWORLD":
                self.play(FadeIn(subtitles[major_split]))
                time_anim = [FadeIn(chart_times[major_split])]
            else:
                self.play(FadeTransform(subtitles[last_major_split], subtitles[major_split]))
                time_anim = FadeTransform(chart_times[last_major_split], chart_times[major_split])
            last_major_split = major_split
            self.play(LaggedStart(*animations, lag_ratio=0.01), time_anim)
            self.wait()
            self.play(Circumscribe(charts[41]), run_time=2)
            self.wait()


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -p -o {name}.mp4 {name}.py {name.capitalize()}")
