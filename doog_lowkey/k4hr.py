import json
from math import isnan
import math
import random
from manim import *
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
from rankedutils import numb, word

ROOT = Path(__file__).parent
player = None
season = None

X_MIN = 300
X_MAX = 780
X_STEP = 20
CLASSES = int((X_MAX - X_MIN) / X_STEP)
ROOT = Path(__file__).resolve().parent
PERCENTILES = [5, 20, 50, 80, 95]
times = {
    "doogile": [
        ["00:20:56", "20:22.123"],
        ["00:52:28", "31:10.073"],
        ["01:05:34", "12:40.585"],
        ["01:35:47", "24:04.249"],
        ["01:54:37", "17:04.570"],
        ["02:08:14", "12:42.456"],
        ["02:25:00", "12:18.514"],
        ["02:41:22", "14:38.628"],
        ["02:57:55", "15:06.032"],
        ["03:16:49", "17:02.730"],
        ["03:31:03", "13:02.168"],
        ["03:44:29", "13:14.953"],
    ],
    "Lowk3y_": [
        ["00:14:06", "13:56.745"],
        ["00:41:36", "12:48.496"],
        ["00:55:16", "13:13.546"],
        ["01:16:02", "14:26.461"],
        ["01:37:33", "18:29.322"],
        ["01:59:33", "21:45.422"],
        ["02:33:12", "15:14.244"],
        ["03:08:19", "12:48.288"],
        ["03:21:59", "11:12.434"],
        ["03:33:20", "11:03.929"],
        ["03:55:55", "10:57.628"],
    ]
}


class Plot(Scene):

    def construct(self):
        # Theme
        Text.set_default(font="Minecraft")

        player = "Lowk3y_"

        # Title
        title = Text(f"{player.capitalize()}", font_size=24)
        title.to_edge(UP, buff=0.7)

        total_igt = int(sum(word.get_raw_time(time[:5]) for time in (tim[1] for tim in times[player])) / 1000)
        total_time = 60 * 60 * 4
        reset_time = total_time - total_igt
        print(reset_time / 60, total_igt / 60)



if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py {name.capitalize()}")
