from manim import *
import pandas as pd
import os
import numpy as np
import math

SIZE = 4
SECTORS = 12
SUB_CIRCLES = 16


class VeinRoseDiagram(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        df = pd.read_csv(os.path.join("random", "sarah", "naddy2.csv"))
        inverse_bearings = [(180 + bearing) % 360 for bearing, _ in df.values]
        max_sizes = [max_size for _, max_size in df.values]
        inverse_df = pd.DataFrame(
            {
                "bearing": inverse_bearings,
                "max size": max_sizes,
            }
        )
        df = pd.concat([df, inverse_df]).sort_values(by="max size", ascending=False)

        vein_array = [[] for _ in range(SECTORS)]
        for i in range(SECTORS):
            min_bearing = 360 * i / SECTORS
            max_bearing = 360 * (i + 1) / SECTORS

            for bearing, max_size in df.values:
                if not min_bearing <= bearing < max_bearing:
                    continue

                inner_radius = SIZE * len(vein_array[i]) / SUB_CIRCLES
                outer_radius = SIZE * (len(vein_array[i]) + 1) / SUB_CIRCLES
                fill_color = ManimColor.from_rgb(
                    (
                        255 - min(max_size * 3, 255),
                        255 - min(70 + max_size * 5, 255),
                        255,
                    )
                )
                start_angle = - 2 * math.pi * (i + 4) / SECTORS
                angle = 2 * math.pi / SECTORS
                sector = Sector(
                    inner_radius=inner_radius,
                    outer_radius=outer_radius,
                    fill_color=fill_color,
                    start_angle=start_angle,
                    angle=angle,
                )
                vein_array[i].append(max_size)
                self.add(sector)

        circle = Circle(
            radius=SIZE,
            color=ManimColor((0, 0, 0)),
        )
        self.add(circle)

        for i in range(SECTORS):
            pos_x = SIZE * np.cos(- 2 * math.pi * (i - 3) / SECTORS)
            pos_y = SIZE * np.sin(- 2 * math.pi * (i - 3) / SECTORS)
            line = Line(
                (0, 0, 0),
                (pos_x, pos_y, 0),
                color=ManimColor((0, 0, 0), 0.1),
                stroke_width=1,
            )
            self.add(line)

            label_text = f"{int(360 * i / SECTORS)}°"
            text_pos_x = 1.15 * pos_x
            text_pos_y = 1.15 * pos_y
            label = Text(
                label_text,
                color=BLACK,
                font="Arial",
                font_size=32,
            ).move_to([
                text_pos_x, text_pos_y, 0
            ])
            self.add(label)

        for i in range(SUB_CIRCLES):
            radius = SIZE * i / SUB_CIRCLES
            sub_circle = Circle(
                radius=radius,
                color=ManimColor((127, 127, 127), 0.1),
                stroke_width=1,
            )
            self.add(sub_circle)

        key_sizes = [
            0.1,
            5,
            10,
            25,
            50,
            100,
        ]
        for i, key in enumerate(key_sizes):
            fill_color = ManimColor.from_rgba(
                (
                    255 - min(key * 3, 255),
                    255 - min(70 + key * 5, 255),
                    255,
                ),
            )
            square = Square(
                side_length=0.3,
                color=BLACK,
                stroke_width=4,
            ).move_to([
                -6.5,
                i * 0.5 - 6.5,
                0
            ])
            square.set_fill(fill_color, opacity=1)
            self.add(square)

            label_text = f"{key}cm"
            label = Text(
                label_text,
                color=BLACK,
                font="Arial",
                font_size=24,
            ).move_to(
                [
                    -6,
                    i * 0.5 - 6.5,
                    0
                ],
                aligned_edge=LEFT,
            )
            self.add(label)

        key_title = Text(
            "Maximum Vein Size",
            color=BLACK,
            font="Arial",
            font_size=28,
        ).move_to(
            [
                -6.7,
                -3.5,
                0
            ],
            aligned_edge=LEFT,
        )
        self.add(key_title)

        diagram_title = Text(
            "Orientations of Quartz Veins",
            color=BLACK,
            font="Arial",
            font_size=48,
        ).move_to(
            [
                0,
                6.5,
                0
            ],
            aligned_edge=UP,
        )
        self.add(diagram_title)



# Execute rendering
if __name__ == "__main__":
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 1440,1440 -o VeinRoseDiagram.png .\random\sarah\sarah.py VeinRoseDiagram")