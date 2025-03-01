from datetime import timedelta
import json
from pathlib import Path
from manim import *
import pandas as pd
import os


RANKS = ["coal", "iron", "gold", "emerald", "diamond", "netherite"]
BASTIONS = ["bridge", "housing", "stables", "treasure"]


class Plot(ThreeDScene):

    def construct(self):
        data_file = Path(__file__).parent / "data" / "bastion_pace.json"
        with open(data_file, "r") as f:
            data = json.load(f)

        ax = ThreeDAxes(
            x_range=[0, 7, 1],
            y_range=[0, 4, 1],
            z_range=[0, 8, 1],
            x_length=7,
            y_length=4,
            z_length=8
        )

        labels = ax.get_axis_labels(
            Tex("Rank").scale(0.5),
            Tex("Bastion").scale(0.5),
            Tex("Speed").scale(0.5)
        )

        self.add(ax, labels)

        # Adding tick labels for x and y axes
        x_ticks = [Tex(rank).scale(0.4).rotate(0.5*PI).next_to(ax.c2p(x+1, 0, 0), DOWN) for x, rank in enumerate(RANKS)]
        y_ticks = [Tex(split).scale(0.4).rotate(PI).next_to(ax.c2p(0, y+1, 0), LEFT) for y, split in enumerate(BASTIONS)]

        self.add(*x_ticks, *y_ticks)

        # Iterate through rows of the dataframe
        bars = VGroup()
        z_scale = 240000

        for x, rank in enumerate(RANKS):
            for y, bastion in enumerate(BASTIONS):
                z = data[bastion]["rank_means"][rank]
                bar = Prism(
                    dimensions=[0.5, 0.5, z / z_scale],
                    fill_color=ManimColor.from_rgb((int(x * 40), 50, int(y * 30)), 1.0),
                    fill_opacity=0.7
                )
                bar.shift(RIGHT * x + UP * y + OUT * z / z_scale / 2)
                bars.add(bar)

            x += 1
        bars.shift(LEFT * 2.5 + DOWN * 1)
        # Add the bars to the scene

        self.add(bars)

        # # Set camera orientation
        self.set_camera_orientation(phi=60 * DEGREES, theta=-30 * DEGREES)
        # self.wait(1)
        # self.begin_ambient_camera_rotation(0.4)
        # self.play(Write(bars))
        # self.wait(16)
        # self.stop_ambient_camera_rotation()


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
