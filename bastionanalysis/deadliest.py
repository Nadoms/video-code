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

        title = Text("Mean Bastion Death Rates For Each Rank", font_size=28)
        title.move_to(ORIGIN).shift(UP * 5.5).rotate(PI / 4, axis=RIGHT)

        bastions = list(data.keys())
        ranks = list(data[bastions[0]]["rank_death_rates"].keys())
        x_length = len(ranks) + 1
        y_length = len(bastions) + 1
        chart = ThreeDAxes(
            x_range=[0, x_length, 1],
            y_range=[0, y_length, 1],
            z_range=[0, 60, 10],
            x_length=x_length,
            y_length=y_length,
            z_length=3,
        ).shift(0.5 * IN)

        bars = VGroup()
        bar_labels = VGroup()
        y = 1
        for bastion in bastions:
            x = 1
            for rank, death_rate in data[bastion]["rank_death_rates"].items():
                fill_color = ManimColor.from_rgb(
                    (death_rate * 1.1, (0.6 - death_rate) * 0.7, (0.6 - death_rate) * 1.7),
                    1.0,
                )
                stroke_color = ManimColor.from_rgb(
                    (0.3 + death_rate * 1.1, (1 - death_rate) * 0.7, (1 - death_rate)),
                    1.0,
                )
                bar = Prism(
                    dimensions=[0.5, 0.5, death_rate * 5],
                    fill_color=fill_color,
                    stroke_color=stroke_color,
                    stroke_width=1,
                    fill_opacity=0.8,
                ).move_to(chart.c2p(x, y, 0), aligned_edge=IN)
                bar_label = Text(
                    f"{round(death_rate * 100, 1)}%",
                    font_size=9,
                ).next_to(bar, OUT).shift(0.25 * IN)
                bars.add(bar)
                bar_labels.add(bar_label)
                x += 1
            y += 1

        grid = VGroup()
        tick_labels = VGroup()
        for x in range(1, x_length):
            line = Line(
                start=chart.c2p(x, 0, 0),
                end=chart.c2p(x, y_length, 0),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            tick_label = Text(ranks[x-1], font_size=14).next_to(chart.c2p(x, 0, 0), DOWN)
            grid.add(line)
            tick_labels.add(tick_label)
        for y in range(1, y_length):
            line = Line(
                start=chart.c2p(0, y, 0),
                end=chart.c2p(x_length, y, 0),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            tick_label = Text(bastions[y-1], font_size=14).next_to(chart.c2p(0, y, 0), LEFT)
            grid.add(line)
            tick_labels.add(tick_label)
        for z in range(0, 6):
            tick_label = Text(f"{z * 10}%").scale(0.4).rotate(0.5 * PI, axis=RIGHT).next_to(chart.c2p(0, 0, z * 10), LEFT)
            # tick_labels.add(tick_label)

        labels = chart.get_axis_labels(
            Text("Rank", font_size=18),
            Text("Bastion", font_size=18).rotate(-0.5 * PI),
            Text("", font_size=18),
        )

        phi = 50 * DEGREES
        theta = -130 * DEGREES
        self.set_camera_orientation(phi=phi, theta=theta)
        self.begin_ambient_camera_rotation(0.02)
        self.play(Write(title))
        self.play(Write(chart), Write(grid), Write(bars))
        self.play(Write(labels), Write(tick_labels))
        self.wait()
        self.play(Write(bar_labels))
        self.wait(duration=32)


# Execute rendering
if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(fr"manim -qk -v WARNING -p --disable_caching -r 1920,1080 -o {name}.mp4 {name}.py Plot")
