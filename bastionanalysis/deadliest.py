from datetime import timedelta
import json
from pathlib import Path
from manim import *
import pandas as pd
import os


class Plot(ThreeDScene):

    def construct(self):
        data_file = Path(__file__).parent / "data" / "bastion_pace.json"
        with open(data_file, "r") as f:
            data = json.load(f)

        title = Text("Mean Bastion Death Rates For Each Rank", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        bastions = list(data.keys())
        ranks = list(data[bastions[0]]["rank_death_rates"].keys())
        x_length = len(bastions) + 1
        y_length = len(ranks) + 1
        chart = ThreeDAxes(
            x_range=[0, x_length, 1],
            y_range=[0, y_length, 1],
            z_range=[0, 100, 10],
            x_length=x_length,
            y_length=y_length,
            z_length=5,
        )

        bars = VGroup()
        bar_labels = VGroup()
        x = 1
        for bastion in data:
            y = 1
            for rank, death_rate in data[bastion]["rank_death_rates"].items():
                bar = Prism(
                    dimensions=[0.5, 0.5, death_rate * 10],
                    fill_color=ManimColor.from_rgb(
                        (death_rate * 1.3, (0.6 - death_rate) * 1.7, (0.6 - death_rate) * 0.7),
                        1.0,
                    ),
                    fill_opacity=0.7,
                ).move_to(chart.c2p(x, y, 0), aligned_edge=IN)
                bar_label = Tex(f"{death_rate}%").scale(0.5).next_to(bar, OUT)
                bars.add(bar)
                bar_labels.add(bar_label)
                y += 1
            x += 1

        grid = VGroup()
        tick_labels = VGroup()
        for x in range(1, x_length):
            line = Line(
                start=chart.c2p(x, 0, 0),
                end=chart.c2p(x, y_length, 0),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            tick_label = Tex(bastions[x-1]).scale(0.4).rotate(0.5 * PI).next_to(chart.c2p(x, 0, 0), DOWN)
            grid.add(line)
            tick_labels.add(tick_label)
        for y in range(1, y_length):
            line = Line(
                start=chart.c2p(0, y, 0),
                end=chart.c2p(x_length, y, 0),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            tick_label = Tex(ranks[y-1]).scale(0.4).rotate(0.5 * PI).next_to(chart.c2p(0, y, 0), LEFT)
            grid.add(line)
            tick_labels.add(tick_label)

        labels = chart.get_axis_labels(
            Tex("Bastion").scale(0.5),
            Tex("Rank").scale(0.5),
            Tex("Death Rate").scale(0.5),
        )

        phi = 70 * DEGREES
        theta = -35 * DEGREES
        self.set_camera_orientation(phi=phi, theta=theta, zoom=0.9)
        self.play(Write(title))
        self.play(Write(chart), Write(grid), Write(labels), Write(tick_labels))
        self.play(Write(bars))
        self.begin_ambient_camera_rotation(0.4)
        self.wait()
        self.play(Write(bar_labels))
        self.wait(duration=8)


# Execute rendering
if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(fr"manim -qk -v WARNING -p --disable_caching -r 1920,1080 -o {name}.mp4 {name}.py Plot")
