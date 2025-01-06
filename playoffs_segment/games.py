from io import BytesIO
import json
from manim import *
import os
from pathlib import Path
from PIL import Image
import requests


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
Y_MIN = 0
Y_MAX = 2000
STEP = 200
TIME_PER_GAME = 16.2


class Games(Scene):

    def construct(self):
        # Data
        data_file = DATA_DIR / "players.json"
        with open(data_file, "r") as f:
            data = json.load(f)
        players = list(data.keys())
        player_count = len(players)
        values = [data[player]["games"] for player in players]

        # Title
        title = Text("Playoffs Competitors - Season 6 Games", font_size=24)
        title.move_to(ORIGIN).shift(UP * 3)

        # Chart
        chart = BarChart(
            values=values,
            y_range=[Y_MIN, Y_MAX, STEP],
            axis_config={"font_size": 20}
        )

        # Axes labels
        labels = chart.get_axis_labels(
            Tex("Player").scale(0.5),
            Tex("Games Played (S6)").scale(0.5)
        )

        # Horizontal grid lines
        lines = VGroup()
        for y in range(Y_MIN, Y_MAX, STEP):
            line = Line(
                start=chart.c2p(0, y + STEP),
                end=chart.c2p(player_count, y + STEP),
                stroke_color=WHITE,
                stroke_opacity=0.1
            )
            lines.add(line)

        # Player icons
        bars = chart.bars
        player_icons = Group()
        for player, bar in zip(players, bars):
            if not (ASSETS_DIR / f"{player}.png").exists():
                image = requests.get(f"https://mc-heads.net/avatar/{player}").content
                image = Image.open(BytesIO(image))
                image.save(ASSETS_DIR / f"{player}.png")
            player_icon = ImageMobject(ASSETS_DIR / f"{player}.png")
            player_icon.scale(0.4).next_to(bar, DOWN)
            player_icons.add(player_icon)

        # Bar value labels
        bar_labels = VGroup()
        for value, bar in zip(values, bars):
            bar_label = Text(str(value)).scale(0.35).next_to(bar, UP * 0.5)
            bar_labels.add(bar_label)
            color_value = (value - Y_MIN) / (Y_MAX - Y_MIN)
            color_value = max(0, min(color_value, 1))
            fill_color = interpolate_color(
                DARK_BLUE,
                LIGHTER_GRAY,
                color_value,
            )
            outline_color = WHITE
            bar.set_fill(fill_color, opacity=0.7)
            bar.set_stroke(outline_color, width=3)

        # Animation
        self.play(Write(title))
        self.play(Write(chart))
        self.play(Write(labels), Write(lines))
        self.play(FadeIn(player_icons))
        self.wait()
        self.play(Write(bar_labels))
        self.wait()


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 1440,1080 -o {name}.mp4 {name}.py {name.capitalize()}")
