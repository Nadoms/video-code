import json
from math import isnan
import random
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
X_STEP = 10


class Plot(Scene):

    def construct(self):
        DEFAULT_STROKE_WIDTH = 3
        # Data
        split_data_points = {
            "overworld": [],
            "nether": [],
            "bastion": [],
            "fortress": [],
            "blind": [],
            "stronghold": [],
        }
        po_split_data_points = {
            "overworld": [],
            "nether": [],
            "bastion": [],
            "fortress": [],
            "blind": [],
            "stronghold": [],
        }
        scaled_split_data_points = {
            "overworld": [],
            "nether": [],
            "bastion": [],
            "fort-blind": [],
            "stronghold": [],
        }
        scaled_po_split_data_points = {
            "overworld": [],
            "nether": [],
            "bastion": [],
            "fort-blind": [],
            "stronghold": [],
        }
        with open(DATA_DIR / "disparity.json", "r") as f:
            averages = json.load(f)
        ranked_average = sum(
            averages["ranked"][split] for split in averages["ranked"]
        ) / len(averages["ranked"])
        po_average = sum(
            averages["po"][split] for split in averages["po"]
        ) / len(averages["po"])
        ranked_scaling = {key: ranked_average / value for key, value in averages["ranked"].items()}
        po_scaling = {key: po_average / value for key, value in averages["po"].items()}
        data_file = DATA_DIR / "disparity.csv"
        data_points = pd.read_csv(data_file).values.tolist()
        for elo, _, _, overworld, nether, bastion, fortress, blind, stronghold, fort_blind in data_points:
            if elo == 3000:
                po_split_data_points["overworld"].append(overworld / 1000) if not isnan(overworld) else None
                po_split_data_points["nether"].append(nether / 1000) if not isnan(nether) else None
                po_split_data_points["bastion"].append(bastion / 1000) if not isnan(bastion) else None
                po_split_data_points["fortress"].append(fortress / 1000) if not isnan(fortress) else None
                po_split_data_points["blind"].append(blind / 1000) if not isnan(blind) else None
                po_split_data_points["stronghold"].append(stronghold / 1000) if not isnan(stronghold) else None
                scaled_po_split_data_points["overworld"].append(overworld / 1000 * po_scaling["ow"]) if not isnan(overworld) else None
                scaled_po_split_data_points["nether"].append(nether / 1000 * po_scaling["nether"]) if not isnan(nether) else None
                scaled_po_split_data_points["bastion"].append(bastion / 1000 * po_scaling["bastion"]) if not isnan(bastion) else None
                scaled_po_split_data_points["fort-blind"].append(fort_blind / 1000 * po_scaling["fort-blind"]) if not isnan(fort_blind) else None
                scaled_po_split_data_points["stronghold"].append(stronghold / 1000 * po_scaling["stronghold"]) if not isnan(stronghold) else None
            split_data_points["overworld"].append(overworld / 1000) if not isnan(overworld) else None
            split_data_points["nether"].append(nether / 1000) if not isnan(nether) else None
            split_data_points["bastion"].append(bastion / 1000) if not isnan(bastion) else None
            split_data_points["fortress"].append(fortress / 1000) if not isnan(fortress) else None
            split_data_points["blind"].append(blind / 1000) if not isnan(blind) else None
            split_data_points["stronghold"].append(stronghold / 1000) if not isnan(stronghold) else None
            scaled_split_data_points["overworld"].append(overworld / 1000 * ranked_scaling["ow"]) if not isnan(overworld) else None
            scaled_split_data_points["nether"].append(nether / 1000 * ranked_scaling["nether"]) if not isnan(nether) else None
            scaled_split_data_points["bastion"].append(bastion / 1000 * ranked_scaling["bastion"]) if not isnan(bastion) else None
            scaled_split_data_points["fort-blind"].append(fort_blind / 1000 * ranked_scaling["fort-blind"]) if not isnan(fort_blind) else None
            scaled_split_data_points["stronghold"].append(stronghold / 1000 * ranked_scaling["stronghold"]) if not isnan(stronghold) else None

        split_box_plot = {
            split: [
                min(split_data_points[split]),
                np.percentile(split_data_points[split], 25),
                np.median(split_data_points[split]),
                np.percentile(split_data_points[split], 75),
                max(split_data_points[split]),
            ] if split_data_points[split] else None
            for split in split_data_points
        }
        po_split_box_plot = {
            split: [
                min(po_split_data_points[split]),
                np.percentile(po_split_data_points[split], 25),
                np.median(po_split_data_points[split]),
                np.percentile(po_split_data_points[split], 75),
                max(po_split_data_points[split]),
            ] if po_split_data_points[split] else None
            for split in po_split_data_points
        }
        scaled_split_box_plot = {
            split: [
                min(scaled_split_data_points[split]),
                np.percentile(scaled_split_data_points[split], 25),
                np.median(scaled_split_data_points[split]),
                np.percentile(scaled_split_data_points[split], 75),
                max(scaled_split_data_points[split]),
            ] if scaled_split_data_points[split] else None
            for split in scaled_split_data_points
        }
        scaled_po_split_box_plot = {
            split: [
                min(scaled_po_split_data_points[split]),
                np.percentile(scaled_po_split_data_points[split], 25),
                np.median(scaled_po_split_data_points[split]),
                np.percentile(scaled_po_split_data_points[split], 75),
                max(scaled_po_split_data_points[split]),
            ] if scaled_po_split_data_points[split] else None
            for split in scaled_po_split_data_points
        }

        # Title
        Text.set_default(font="Minecraft")
        title = Text("Split Disparity", font_size=28)
        title.move_to(ORIGIN).shift(UP * 3.5)
        scaled_title = Text("Split Disparity (SCALED)", font_size=28)
        scaled_title.move_to(ORIGIN).shift(UP * 3.5)
        # Subtitles
        general_title = Text("Across all S7 (and some S8) games", font_size=18)
        general_title.next_to(title, DOWN, buff=0.1)
        po_title = Text("In all playoffs matches", font_size=18)
        po_title.next_to(title, DOWN, buff=0.1)

        # Axes
        axes = Axes(
            x_range=[X_MIN, X_MAX, X_STEP],
            y_range=[0, 6, 1],
            x_length=11,
            y_length=6,
            axis_config={
                "include_numbers": False,
                "include_tip": False,
            },
        )

        # X Labels
        x_labels = VGroup()
        for x in range(X_MIN, X_MAX, X_STEP):
            label_str = digital_time(x)
            label = Text(label_str).scale(0.35).next_to(
                axes.x_axis.n2p(x), DOWN, buff=0.2
            )
            x_labels.add(label)

        gridlines = VGroup(
            Line(
                start=axes.c2p(x, 0),
                end=axes.c2p(x, 6),
                stroke_width=1,
            ) for x in range(X_MIN, X_MAX, 5)
        )
        even = True
        for line in gridlines:
            if even:
                line.set_opacity(0.2)
            else:
                line.set_opacity(0.1)
            even = not even

        # Axes labels
        labels = axes.get_axis_labels(
            Tex("Pace Difference (s)").scale(0.5),
            Tex("Split Type").scale(0.5)
        )

        # Dots n boxes
        box_width = 0.3
        def create_boxplot(data, y_pos, color, label):
            min_val, q1, median, q3, max_val = data
            y_pos = axes.y_axis.n2p(y_pos)[1]

            lower_whisker = Line(
                start=axes.c2p(min_val, y_pos - box_width * 0.4),
                end=axes.c2p(min_val, y_pos + box_width * 0.4)
            )
            lower_whisker_hor = Line(
                start=axes.c2p(q1, y_pos),
                end=axes.c2p(min_val, y_pos)
            )
            upper_whisker_hor = Line(
                start=axes.c2p(q3, y_pos),
                end=axes.c2p(max_val, y_pos)
            )
            upper_whisker = Line(
                start=axes.c2p(max_val, y_pos - box_width * 0.4),
                end=axes.c2p(max_val, y_pos + box_width * 0.4)
            )
            median_line = Line(
                start=axes.c2p(median, y_pos - box_width * 0.7),
                end=axes.c2p(median, y_pos + box_width * 0.7),
                color=YELLOW
            )
            lower_whisker.set_opacity(0.5)
            lower_whisker_hor.set_opacity(0.5)
            upper_whisker_hor.set_opacity(0.5)
            upper_whisker.set_opacity(0.5)
            box = Rectangle(
                width=axes.x_length * (q3 - q1) / (X_MAX - X_MIN),
                height=box_width,
                stroke_color=color,
                fill_color=color,
                fill_opacity=0.2,
            ).move_to(axes.c2p((q1 + q3) / 2, y_pos))
            lab = Text(label, font_size=15).next_to(lower_whisker, LEFT)
            return VGroup(box, lower_whisker, lower_whisker_hor, upper_whisker, upper_whisker_hor, median_line, lab)

        dots = VGroup()
        boxes = VGroup()
        for i, split in enumerate(reversed(split_box_plot)):
            case_group = create_boxplot(split_box_plot[split], (i + 3.5), BLUE, split)
            boxes.add(case_group)

            for j, disp in enumerate(split_data_points[split]):
                if j % 100 == 0:
                    print(j)
                    colour_scale = min(disp / 120, 1)
                    colour = ManimColor.from_rgb((colour_scale * 255, 127, 255 - colour_scale * 255))
                    dot = Dot(axes.c2p(disp, i + 0.5 + (random.random() - 0.5) / 10), color=colour, radius=0.01)
                    dots.add(dot)
        po_dots = VGroup()
        po_boxes = VGroup()
        for i, split in enumerate(reversed(po_split_box_plot)):
            case_group = create_boxplot(po_split_box_plot[split], (i + 3.5), BLUE, split)
            po_boxes.add(case_group)

            for j, disp in enumerate(po_split_data_points[split]):
                print(j)
                colour_scale = min(disp / 120, 1)
                colour = ManimColor.from_rgb((colour_scale * 255, 127, 255 - colour_scale * 255))
                dot = Dot(axes.c2p(disp, i + 0.5 + (random.random() - 0.5) / 10), color=colour, radius=0.02)
                po_dots.add(dot)
        scaled_dots = VGroup()
        scaled_boxes = VGroup()
        for i, split in enumerate(reversed(scaled_split_box_plot)):
            case_group = create_boxplot(scaled_split_box_plot[split], (i + 3.5), BLUE, split)
            scaled_boxes.add(case_group)

            for j, disp in enumerate(scaled_split_data_points[split]):
                if j % 100 == 0:
                    print(j)
                    colour_scale = min(disp / 120, 1)
                    colour = ManimColor.from_rgb((colour_scale * 255, 127, 255 - colour_scale * 255))
                    dot = Dot(axes.c2p(disp, i + 0.5 + (random.random() - 0.5) / 10), color=colour, radius=0.01)
                    scaled_dots.add(dot)
        scaled_po_dots = VGroup()
        scaled_po_boxes = VGroup()
        for i, split in enumerate(reversed(scaled_po_split_box_plot)):
            case_group = create_boxplot(scaled_po_split_box_plot[split], (i + 3.5), BLUE, split)
            scaled_po_boxes.add(case_group)

            for j, disp in enumerate(scaled_po_split_data_points[split]):
                print(j)
                colour_scale = min(disp / 120, 1)
                colour = ManimColor.from_rgb((colour_scale * 255, 127, 255 - colour_scale * 255))
                dot = Dot(axes.c2p(disp, i + 0.5 + (random.random() - 0.5) / 10), color=colour, radius=0.02)
                scaled_po_dots.add(dot)

        # Animation
        self.play(Write(axes), Write(title), Write(gridlines))
        self.play(Write(labels), Write(general_title), Write(x_labels))
        self.play(Write(boxes))
        self.play(Write(dots))
        self.wait()
        self.play(Unwrite(boxes), Unwrite(dots), Unwrite(title))
        self.play(Write(scaled_boxes), Write(scaled_title))
        self.play(Write(scaled_dots))
        self.wait()
        self.play(Unwrite(scaled_boxes), Unwrite(scaled_dots), Unwrite(general_title))
        self.play(Write(scaled_po_boxes), Write(po_title))
        self.play(Write(scaled_po_dots))
        self.wait()


def digital_time(raw_time):
    time = str(timedelta(seconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 2560,1440 -o {name}.mp4 {name}.py {name.capitalize()}")
