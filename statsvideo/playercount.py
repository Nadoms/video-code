from manim import *
import pandas as pd
import os


class PlayerCount(Scene):

    def construct(self):
        data_file = os.path.join("statsvideo", "data", "playercount.csv")
        df = pd.read_csv(data_file)

        values = df.iloc[0]
        bar_names = ["S0", "S1", "S2", "S3", "S4", "S5"]
        chart = BarChart(bar_names=bar_names,
                        values=values,
                        y_range=[0, 8000, 2000],
                        axis_config={"font_size": 20}
        )

        labels = chart.get_axis_labels(
            Tex("Season").scale(0.5),
            Tex("Player Count").scale(0.5)
        )

        self.play(Write(chart))
        self.play(Write(labels))

        self.wait(duration=2)

        group = VGroup(chart, labels)

        self.play(group.animate.scale(0.4))
        self.play(group.animate.shift(5.5*LEFT))

        
        data_file = os.path.join("statsvideo", "data", "playercount.csv")
        df = pd.read_csv(data_file)

        matches = df.iloc[1]
        days = df.iloc[2]
        values = matches / days
        bar_names = ["S0", "S1", "S2", "S3", "S4", "S5"]
        chart = BarChart(bar_names=bar_names,
                        values=values,
                        y_range=[0, 2500, 500],
                        axis_config={"font_size": 20}
        )

        labels = chart.get_axis_labels(
            Tex("Season").scale(0.5),
            Tex("Matches per Day").scale(0.5)
        )

        self.play(Write(chart))
        self.play(Write(labels))

        self.wait(duration=2)


# Execute rendering
if __name__ == "__main__":
    # os.system(r"manim -qk -v WARNING -p --disable_caching -r 1280,720 -o PlayerCount.mp4 .\statsvideo\playercount.py PlayerCount")
    os.system(r"manim -qk -v WARNING -p --disable_caching -r 1280,720 -o MatchCount.mp4 .\statsvideo\playercount.py MatchCount")