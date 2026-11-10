import math
from manim import *
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"


class Plot(Scene):

    def construct(self):
        # Theme
        Text.set_default(font="Minecraft")

        self.play()


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py {name.capitalize()}")
