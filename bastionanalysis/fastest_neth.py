from datetime import timedelta
import json
from pathlib import Path
from manim import *
import pandas as pd
import os


class Plot(Scene):

    def construct(self):
        data_file = Path(__file__).parent / "data" / "bastion_pace.json"
        with open(data_file, "r") as f:
            data = json.load(f)

        title = Text("Mean Bastion Split Times at 2000+ Elo", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        bar_names = list(data.keys())
        values = [data[bastion]["rank_means"]["netherite"] for bastion in data]
        minutes = [value / 60000 for value in values]
        chart = BarChart(
            bar_names=bar_names,
            values=minutes,
            y_range=[0, 4, 1],
            axis_config={"font_size": 20}
        )

        lines = VGroup()
        for y in range(0, 5):
            line = Line(
                start=chart.c2p(0, y),
                end=chart.c2p(4, y),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            lines.add(line)

        labels = chart.get_axis_labels(
            Tex("Bastion").scale(0.5),
            Tex("Split Time (min)").scale(0.5)
        )

        self.play(Write(title))
        self.play(Write(chart), Write(lines), Write(labels))

        self.wait()

        bars = chart.get_bars()
        for i, bar in enumerate(bars):
            bar_time = digital_time(values[i])
            bar_label = Tex(f"{bar_time}").scale(0.5).next_to(bar, UP)
            self.play(Write(bar_label))

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
