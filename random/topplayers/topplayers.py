from manim import *
import pandas as pd
import os
import numpy as np
import math

x_min = 5
x_max = 20
player_count = 50


def get_player_comps():
    top_players = []
    ranks = {}
    with open(os.path.join("random", "topplayers", "topplayers.txt")) as f:
        i = 1
        while True:
            line = f.readline().strip().replace("\\", "")
            if not line:
                break
            top_players.append(line)
            ranks[line] = (str(i))
            i += 1

    player_comps = {}
    with open(os.path.join("random", "topplayers", "topavg.txt")) as f:
        while True:
            line = f.readline().strip().replace("\\", "")
            if not line:
                break
            name, time = line.split()
            time = int(time) / 1000 / 60
            if name not in player_comps and name in top_players:
                player_comps[name] = [time]
            elif name in player_comps:
                player_comps[name].append(time)
    return player_comps, ranks


class TopPlayers(Scene):
    def construct(self):
        player_bounds = {}
        player_comps, ranks = get_player_comps()

        for player in player_comps.keys():
            player_bounds[player] = np.quantile(player_comps[player], [0,0.25,0.5,0.75,1])

        player_bounds = {key: value for key, value in sorted(player_bounds.items(), key=lambda item: item[1][2])}

        box_width = 0.3

        # Create axes
        axes = Axes(
            x_range=[x_min, x_max, 1],
            y_range=[0, len(player_comps.keys()), 1],
            x_length=12,
            y_length=player_count * 0.8,
            axis_config={
                "color": BLUE,
                "include_numbers": True,
                "numbers_to_include":[0, 5, 10, 15, 20, 25],
            },
        )
        axes.get_y_axis().set_opacity(0)
        self.add(axes)

        gridlines = [
            Line(
                start=axes.c2p(x, 0),
                end=axes.c2p(x, 1000)
            ) for x in range(5, 21)
        ]
        for line in gridlines:
            line.set_opacity(0.1)
        gridlines = VGroup(*gridlines)
        self.add(gridlines)

        # Function to create a boxplot
        def create_boxplot(data, y_pos, color, label):
            min_val, q1, median, q3, max_val = data

            lower_whisker = Line(
                start=axes.c2p(min_val, y_pos - box_width * 0.4),
                end=axes.c2p(min_val, y_pos + box_width * 0.4)
            )
            lower_whisker_hor = Line(
                start=axes.c2p(q1, y_pos),
                end=axes.c2p(min_val, y_pos)
            )
            upper_whisker_hor = Line(
                start=axes.c2p(q3, y_pos),
                end=axes.c2p(max_val, y_pos)
            )
            upper_whisker = Line(
                start=axes.c2p(max_val, y_pos - box_width * 0.4),
                end=axes.c2p(max_val, y_pos + box_width * 0.4)
            )
            median_line = Line(
                start=axes.c2p(median, y_pos - box_width / 0.8),
                end=axes.c2p(median, y_pos + box_width * 0.8),
                color=YELLOW
            )
            lower_whisker.set_opacity(0.5)
            lower_whisker_hor.set_opacity(0.5)
            upper_whisker_hor.set_opacity(0.5)
            upper_whisker.set_opacity(0.5)
            box = Rectangle(
                width=axes.x_length * (q3 - q1) / (x_max - x_min),
                height=box_width,
                stroke_color=color,
                fill_color=color,
                fill_opacity=0.3,
            ).move_to(axes.c2p((q1 + q3) / 2, y_pos))
            lab = Text(label, font_size=15).next_to(lower_whisker, LEFT)
            return VGroup(box, lower_whisker, lower_whisker_hor, upper_whisker, upper_whisker_hor, median_line, lab)

        # Plotting each boxplot
        dots = VGroup()
        boxes = VGroup()
        for i, player in enumerate(player_bounds.keys()):
            tag = f"{player} #{ranks[player]}"
            case_group = create_boxplot(player_bounds[player], (i + 1), BLUE, tag)
            boxes.add(case_group)

            for time in player_comps[player]:
                if time >= 30:
                    continue
                colour = ManimColor.from_rgb((min(int((time) * 10), 255), 255, min(int((30 - time) * 15), 255), 1.0))
                dot = Dot(axes.c2p(time, i + 1), color=colour, radius=0.02)
                dots.add(dot)

        self.add(boxes)
        self.add(dots)


# Execute rendering
if __name__ == "__main__":
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 1920,{120*player_count} -o TopPlayers.png .\random\topplayers\topplayers.py TopPlayers")