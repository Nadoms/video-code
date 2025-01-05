from datetime import timedelta
from io import BytesIO
import json
import math
from manim import *
import os
from pathlib import Path
from PIL import Image
import requests


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
X_MIN = 8
X_MAX = 30
STEP = 0.25
CLASSES = int(X_MAX / STEP)
ICON_SIZE = 0.15


class Avg(Scene):

    def construct(self):
        # Data
        data_file = DATA_DIR / "players.json"
        with open(data_file, "r") as f:
            data = json.load(f)
        players = list(data.keys())
        player_count = len(players)
        values = [data[player]["avg"] / 60000 for player in players]

        histogram = [0] * CLASSES
        with open(DATA_DIR / "avg.txt") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                avg = int(line.strip()) / 60000
                avg_class = math.floor((avg - X_MIN) / STEP)
                if 0 <= avg_class < CLASSES:
                    histogram[avg_class] += 1 / STEP

        # Title
        title = Text("Season 6 Average Completion Distribution (5+ Completions)", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        # Bar chart
        chart = BarChart(
            bar_names=[f"{digital_time(i * STEP + X_MIN)}" if i % (2 / STEP) == 0 else "" for i in range(CLASSES)],
            y_range=[0, 200, 25],
            values=histogram,
            axis_config={"font_size": 20},
            x_axis_config={
                "include_ticks": False,
                "include_numbers": False
            }
        )

        # Axes labels
        labels = chart.get_axis_labels(
            Tex("Avg").scale(0.5),
            Tex("Player Density (/min)").scale(0.5)
        )

        # Player icons
        player_histogram = [0] * CLASSES
        bars = chart.get_bars()
        player_icons = Group()
        for value, player in zip(values, players):
            if not (ASSETS_DIR / f"{player}.png").exists():
                image = requests.get(f"https://mc-heads.net/avatar/{player}").content
                image = Image.open(BytesIO(image))
                image.save(ASSETS_DIR / f"{player}.png")
            player_class = math.floor((value - X_MIN) / STEP)
            bar = bars[player_class]
            player_icon = ImageMobject(ASSETS_DIR / f"{player}.png")
            player_icon.scale(ICON_SIZE).next_to(bar, UP * 0.5)
            player_icon.shift(UP * player_histogram[player_class] * (ICON_SIZE + 0.1))
            player_histogram[player_class] += 1
            player_icons.add(player_icon)

        # Animation
        group = Group(title, chart, labels, player_icons)
        self.play(Write(title))
        self.play(Write(chart))
        self.play(Write(labels))
        self.wait()
        self.play(FadeIn(player_icons))
        self.wait()
        self.play(group.animate.scale(1.5).shift(RIGHT * 4))
        self.wait()


def digital_time(raw_time):
    raw_time = int(raw_time)
    time = str(timedelta(minutes=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]

    return time


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 1440,1080 -o {name}.mp4 .\{name}.py {name.capitalize()}")
