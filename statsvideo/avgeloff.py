from manim import *
import pandas as pd
import os


class ScatterPlotScene(Scene):

    def construct(self):
        data_file = os.path.join("statsvideo", "data", "avgeloff.csv")
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
        # data_file = os.path.join("statsvideo", "avgeloff.csv")
        data_file = os.path.join("statsvideo", "data", "avgeloff2.csv")
        df = pd.read_csv(data_file)

        # Animate the creation of Axes
        ax = Axes(x_range=[600, 2400, 100],
                  y_range=[10, 30, 2],
                  tips=True,
                  axis_config={"include_numbers": True, "font_size": 20}
        )

        labels = ax.get_axis_labels(
            Tex("Elo").scale(0.5),
            Tex("Avg Completion (min)").scale(0.5)
        )


        dots = []
        special_dots = []
        players = [[517263, 904],
                   [623818, 2323],
                   [637555, 2202],
                   [1057864, 1256]]

        for avg, elo, ff, loss in df.values:
            if loss == 0:
                ffl = 0
            else:
                ffl = ff / loss * 100
            avg = avg / 1000 / 60
            if avg >= 30:
                continue

            colour = ManimColor.from_rgb((int(ffl * 2.55), 50, int((100-ffl) * 2.55)), 1.0)
            
            if [round(avg * 1000 * 60), elo] in players:
                special_dot  = Dot(ax.c2p(elo, avg), color=colour, radius=0.02)
                special_dots.append(special_dot)

            dot = Dot(ax.c2p(elo, avg), color=colour, radius=0.02)
            dots.append(dot)
        
        group = VGroup(ax, labels, *dots, *special_dots)

        self.play(Write(ax))
        self.play(Write(labels))
        self.wait()
            
        self.play([Write(dot) for dot in dots + special_dots])
        self.wait(duration=2)

        self.play(group.animate.scale(1.3))
        self.play(group.animate.shift(2*RIGHT).shift(DOWN))
        self.wait(duration=4)


        self.play(group.animate.shift(0.5*LEFT).shift(2*UP))
        self.wait(duration=2)
        highlight(self, special_dots[3])
        self.play(group.animate.shift(0.5*RIGHT).shift(UP))
        highlight(self, special_dots[0])

        self.play(group.animate.shift(5*LEFT))
        self.wait(duration=2)
        highlight(self, *special_dots[1:3])
        self.wait(duration=2)


def highlight(self, *mobs):
    self.play([ScaleInPlace(mob, 5) for mob in mobs])
    self.play([Circumscribe(mob, Circle, time_width=1) for mob in mobs] + [Indicate(mob) for mob in mobs])
    self.wait(duration=2)
    self.play([ScaleInPlace(mob, 1/5) for mob in mobs])
    self.wait(duration=2)
    


# Execute rendering
if __name__ == "__main__":
    # os.system(r"manim -qk -v WARNING -p --disable_caching -o ScatterPlotScene.png .\statsvideo\avgeloff.py ScatterPlotScene")
    os.system(r"manim -qk -v WARNING -p --disable_caching -o ScatterPlotScene.mp4 .\statsvideo\avgeloff.py ScatterPlotAnimatedScene")