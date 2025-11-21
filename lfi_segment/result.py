import json
import numpy as np
import math
from manim import *
import os
from pathlib import Path
from rankedutils import numb

ROOT = Path(__file__).resolve().parent
PLAYERS = [
    "v_strid",
    "BeefSalad",
    "bing_pigs",
    "NOHACKSJUSTTIGER",
    "7rowl",
    "silverrruns",
    "hackingnoises",
    "Kxpow",
]


class Plot(Scene):

    def construct(self):
        import os
        PLAYER_OI = os.environ.get("PLAYER")
        PLAYER_INDEX = PLAYERS.index(PLAYER_OI)
        # Theme
        Text.set_default(font="Minecraft Default")

        # Data
        with open(ROOT / "data" / "game_results.json", "r") as f:
            data = json.load(f)

        player_data = data[PLAYER_OI]
        labels = {
            "completion_win": "comp",
            "completion_loss": "opp comp",
            "forfeit_win": "opp ff",
            "forfeit_loss": "ff",
            "draw": "draw",
        }
        colours = {
            "completion_win": BLUE,
            "completion_loss": ORANGE,
            "forfeit_win": GREEN_B,
            "forfeit_loss": RED,
            "draw": GREY_B,
        }

        total = sum(player_data.values())

        # Create pie
        slices = VGroup()
        start_angle = PI / 2
        radius = 2.0
        for key in player_data:
            angle = TAU * (player_data[key] / total) if total > 0 else 0
            if angle > 0:
                s = Sector(radius=radius, start_angle=start_angle, angle=angle)
                mid_angle = angle / 2 + start_angle
                s.set_fill(colours[key], opacity=1)
                s.set_stroke(WHITE, width=4)
                dist = 1 if key in ["completion_win", "completion_loss"] else 1.5
                s_hid = Sector(radius=radius * dist, start_angle=mid_angle, angle=0)
                s_text = Text(f"{player_data[key] / total * 100:.1f}%", color=BLACK).scale(0.40).move_to(s_hid.get_center())
                slices.add(s)
                if player_data[key] != 0:
                    slices.add(s_text)
            start_angle += angle

        # Outer circle outline to emphasize the pie (circle)
        outline = Circle(radius=radius, stroke_width=8, color=WHITE)
        pie = VGroup(slices, outline).center().shift(LEFT * 1.5)

        # Legend
        legend = VGroup()
        for i, key in enumerate(player_data.keys()):
            block = Square().scale(0.15).set_fill(colours[key], opacity=1).set_stroke(width=1)
            block.rotate(-PI / 2)
            label_text = Text(f"{key}: {player_data[key] / total * 100:.1f}%").scale(0.40)
            item = VGroup(block, label_text)
            label_text.next_to(block, RIGHT, buff=0.2)
            item.arrange(RIGHT, buff=0.2, center=False)
            item.shift(DOWN * (i * 0.45))
            legend.add(item)
        legend = legend.next_to(pie, RIGHT, buff=0.8)

        self.add(outline, pie, legend)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    for player in PLAYERS:
        os.system(rf"PLAYER={player} manim -qp -o {name}_{player[:3]} {name}.py {name.capitalize()}")
