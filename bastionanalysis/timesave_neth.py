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

        title = Text("Loot Quality Timesave Per Bastion at 2000+ Elo", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        bar_names = list(data.keys())
        runs = [data[bastion]["high_run"] / 1000 for bastion in data]
        bastions = [data[bastion]["rank_means"]["netherite"] / 1000 for bastion in data]
        diffs = [run - bastion for run, bastion in zip(runs, bastions)]
        worst = max(diffs)
        diffs = [worst - diff for diff in diffs]
        chart = BarChart(
            bar_names=bar_names,
            values=diffs,
            y_range=[0, 10, 2],
            axis_config={"font_size": 20}
        )

        lines = VGroup()
        for y in range(0, 11, 2):
            line = Line(
                start=chart.c2p(0, y),
                end=chart.c2p(4, y),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            lines.add(line)

        labels = chart.get_axis_labels(
            Tex("Bastion").scale(0.5),
            Tex("Timesave (sec)").scale(0.5)
        )

        self.play(Write(title))
        self.play(Write(chart))
        self.play(Write(labels))
        self.play(Write(lines))

        self.wait()

        bars = chart.get_bars()
        for i, bar in enumerate(bars):
            bar_time = diffs[i]
            bar_label = Tex(f"{round(bar_time)}s").scale(0.5).next_to(bar, DOWN)
            # self.play(Write(bar_label))

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
