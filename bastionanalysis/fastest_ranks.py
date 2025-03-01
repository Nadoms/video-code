from datetime import timedelta
import json
from pathlib import Path
from manim import *
import pandas as pd
import os


RANKS = ["coal", "iron", "gold", "emerald", "diamond", "netherite"]
BASTIONS = ["bridge", "housing", "stables", "treasure"]


class Plot(Scene):

    def construct(self):
        data_file = Path(__file__).parent / "data" / "bastion_pace.json"
        with open(data_file, "r") as f:
            data = json.load(f)

        title = Text("Mean Bastion Split Times For Each Rank", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        all_bars = VGroup()
        axes = Axes(
            x_range=[0, len(RANKS) + 1, 1],
            y_range=[0, 8, 1],
            y_axis_config={
                "font_size": 20,
                "include_numbers": True,
                "numbers_to_include": list(range(8))
            },
        )

        x_labels = VGroup()
        for i, rank in enumerate(RANKS, start=1):
            label = Text(rank, font_size=20)
            label.next_to(axes.c2p(i, 0), DOWN)
            x_labels.add(label)

        lines = VGroup()
        for y in range(0, 9):
            line = Line(
                start=axes.c2p(0, y),
                end=axes.c2p(len(RANKS) + 1, y),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            lines.add(line)

        bar_width = 0.2
        colours = [BLUE, GREEN, RED, YELLOW]
        bars_list = []
        for i, rank in enumerate(RANKS):
            bars = VGroup()
            for j, bastion in enumerate(BASTIONS):
                value = data[bastion]["rank_means"][rank] / 60000
                value *= 0.75
                bar = Rectangle(
                    width=bar_width,
                    height=value,
                    fill_color=colours[j],
                    fill_opacity=0.7,
                    stroke_width=1,
                )
                bar.move_to(
                    axes.c2p(i + j * bar_width + 0.7, 0)
                )
                bar.align_to(axes.c2p(0, 0), DOWN)
                bars.add(bar)
                bars_list.append(bar)
            all_bars.add(bars)

        labels = axes.get_axis_labels(
            Tex("Rank").scale(0.5),
            Tex("Route Time (min)").scale(0.5)
        )

        labels.add(x_labels)

        # self.wait(duration=1)
        self.play(Write(title))
        self.play(Write(axes), Write(lines), Write(labels))
        self.play(Write(labels))
        self.play(Write(all_bars))

        bar_labels = VGroup()
        for i, bar in enumerate(bars_list):
            bar_text = BASTIONS[i % 4][0]
            bar_label = Tex(bar_text).scale(0.6).next_to(bar, UP)
            bar_labels.add(bar_label)

        self.play(Write(bar_labels))
        self.wait()

        group = VGroup(axes, labels, lines, all_bars, bar_labels, title)
        self.play(group.animate.scale(1.5))
        self.play(group.animate.shift(UP * 2 + LEFT * 6.2))

        self.wait()


def digital_time(raw_time):
    raw_time = int(raw_time)
    time = str(timedelta(milliseconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


# Execute rendering
if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(fr"manim -qk -v WARNING -p --disable_caching -r 1920,1080 -o {name}.mp4 {name}.py Plot")
