import json
import os
from manim import *
from pathlib import Path
from numpy import isnan
import pandas as pd
from rankedutils import numb


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"


class Plot(Scene):

    def construct(self):
        self.camera.background_color = WHITE
        Line.set_default(color=BLACK)
        Text.set_default(font="Minecraft", color=BLACK)
        Tex.set_default(color=BLACK)
        with open(DATA_DIR / "all_players.json") as f:
            data: dict = json.load(f)

        title = Text("Playoffs Competitors - Overview", font_size=24)
        title.to_edge(UP, buff=-9) #-3

        subtitle = Text("Using Season 8 Data", font_size=18)
        subtitle.next_to(title, DOWN, buff=0.2)

        profiles_box = Rectangle(color=BLACK, height=9.5, width=12.5)
        profiles = Group()
        directions = [UL, UR, LEFT, RIGHT, DL, DR, DL, DR, DL, DR, DL, DR, DL, DR, DL, DR]

        distilled_data = {}
        for name in data:
            bar_data = {
                "peak elo": data[name]["peak_elo"],
                "win / loss": round(data[name]["win_loss"], 2),
                "playtime": data[name]["playtime"],
                "comp rate": int(data[name]["completions"] / data[name]["games"] * 100),
                "best time": data[name]["sb"],
                "avg time": data[name]["avg"],
            }
            distilled_data[name] = bar_data
        data_range = {
            data_type: [
                min(distilled_data[name][data_type] for name in distilled_data) * 0.95
                if data_type not in ["best time", "avg time"]
                else min(distilled_data[name][data_type] for name in distilled_data),
                max(distilled_data[name][data_type] for name in distilled_data)
                if data_type not in ["best time", "avg time"]
                else max(distilled_data[name][data_type] for name in distilled_data) * 1.02
            ] for data_type in bar_data
        }
        print(data_range)
        for i, name in enumerate(data):
            profile = Group()

            box = Rectangle(color=BLACK, height=2, width=4)
            icon = ImageMobject(ASSETS_DIR / f"{name}.png").scale(0.42).align_to(box, UL)
            name_txt = Text(f"#{data[name]['seed']} / {name}", font_size=20).next_to(icon, RIGHT, buff=0.1)
            bar_data_relative = {
                data_type: (distilled_data[name][data_type] - data_range[data_type][0]) / (data_range[data_type][1] - data_range[data_type][0])
                    if data_type not in ["best time", "avg time"]
                    else (data_range[data_type][1] - distilled_data[name][data_type]) / (data_range[data_type][1] - data_range[data_type][0])
                for data_type in data_range
            }
            chart = BarChart(
                list(bar_data_relative.values()),
                x_length=11,
                y_length=3.5,
                y_range=[0, 1, 0.1],
                bar_names=list(bar_data_relative.keys()),
                y_axis_config={"include_ticks": False, "include_numbers": False},
            ).scale(0.3).shift(RIGHT * 0.2, DOWN * 0.1)
            bar_txts = VGroup()
            for j, player_distilled_data in enumerate(distilled_data[name].values()):
                if j in [0, 1]:
                    bar_str = str(player_distilled_data)
                elif j == 3:
                    bar_str = f"{player_distilled_data}%"
                elif j == 2:
                    bar_str = f"{int(player_distilled_data / 60 / 60 / 1000)} h"
                else:
                    bar_str = numb.digital_time(player_distilled_data)
                bar_txt = Text(bar_str, font_size=20).scale(0.4).next_to(chart.bars[j], UP, buff=0.05)
                bar_txts.add(bar_txt)
            profile.add(icon, name_txt, box, chart, bar_txts)
            profile.scale(1.5)
            profile.align_to(profiles_box, directions[i])
            if i >= 6:
                profile.shift(DOWN * (((i - 4) // 2)) * 3.25)
            profiles.add(profile)

        profiles.shift(UP * 7.25) # 1.25

        self.add(title, subtitle)
        self.add(profiles)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py -r 2560,5000 {name.capitalize()}")
