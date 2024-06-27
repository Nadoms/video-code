from manim import *
import pandas as pd
import os


class ScatterPlotScene(Scene):

    def construct(self):
        data_file = os.path.join("statsvideo", "avgeloff.csv")
        df = pd.read_csv(data_file)

        # Add the Axes
        ax = Axes(x_range=[600, 2400, 100],
                  y_range=[10, 30, 2],
                  tips=True,
                  axis_config={"include_numbers": True, "font_size": 20}
        )
        labels = ax.get_axis_labels(
            Tex("Elo").scale(0.5),
            Tex("Avg Completion (min)").scale(0.5)
        )
        self.add(ax, labels)

        # Add the dots
        for avg, elo, ffl in df.values:
            avg = avg / 1000 / 60
            colour = ManimColor.from_rgb((int(ffl * 2.55), 50, int((100-ffl) * 2.55)), 1.0)
            dot = Dot(ax.c2p(elo, avg), color=colour, radius=0.02)
            self.add(dot)


class ScatterPlotAnimatedScene(Scene):

    def construct(self):
        data_file = os.path.join("statsvideo", "avgeloff.csv")
        df = pd.read_csv(data_file)

        # Animate the creation of Axes
        ax = Axes(x_range=[600, 2400, 100],
                  y_range=[10, 30, 2],
                  tips=True,
                  axis_config={"include_numbers": True, "font_size": 20}
        )
        self.play(Write(ax))

        labels = ax.get_axis_labels(
            Tex("Elo").scale(0.5),
            Tex("Avg Completion (min)").scale(0.5)
        )

        self.wait()

        # Animate the creation of dots
        dots = []
        for avg, elo, ffl in df.values:
            avg = avg / 1000 / 60
            colour = ManimColor.from_rgb((int(ffl * 2.55), 50, int((100-ffl) * 2.55)), 1.0)
            dot = Dot(ax.c2p(elo, avg), color=colour, radius=0.02)
            dots.append(dot)
            
        self.play([Write(dot) for dot in dots])
        
        self.play(Write(labels))

        self.wait()


# Execute rendering
if __name__ == "__main__":
    # os.system(r"manim -qk -v WARNING -p --disable_caching -o ScatterPlotScene.png .\statsvideo\avgeloff.py ScatterPlotScene")
    os.system(r"manim -qk -v WARNING -p --disable_caching -o ScatterPlotScene.mp4 .\statsvideo\avgeloff.py ScatterPlotAnimatedScene")