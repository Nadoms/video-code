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


class MatchCount(Scene):

    def construct(self):
        data_file = os.path.join("statsvideo", "data", "playercount.csv")
        df = pd.read_csv(data_file)

        areas = df.iloc[1]
        widths = df.iloc[2]
        rect_names = ["S0", "S1", "S2", "S3", "S4", "S5"]
        rect_colors = ["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600"]
        chart = Axes(x_range=[0, 680, 0],
                    y_range=[0, 2500, 500],
                    x_axis_config={"include_ticks": False,
                                   "include_numbers": False},
                    axis_config={"font_size": 20}
        )

        labels = chart.get_axis_labels(
            Tex("Season").scale(0.5),
            Tex("Match Density").scale(0.5)
        )

        x_offset = 0
        padding = 0.1
        rects = []
        rect_labels = VGroup()
        for i, width in enumerate(widths):
            height = areas[i] / width
            rect = Rectangle(
                width=chart.x_axis.n2p(width)[0] - chart.x_axis.n2p(0)[0] - padding,
                height=chart.y_axis.n2p(height)[1] - chart.y_axis.n2p(0)[1] - padding,
                fill_opacity=0.8,
                fill_color=BLUE,
                stroke_color="#ffffff"
            )
            rect.move_to(chart.c2p(x_offset + width / 2, height/2))
            rects.append(rect)

            rect_label = Text(rect_names[i], font_size=24)
            edge = rect.get_edge_center(DOWN)
            edge[1] -= 0.4
            rect_label.move_to(edge)
            rect_labels.add(rect_label)

            x_offset += width

        chart.add(*rects)
        self.add(chart)
        self.add(labels)
        self.add(rect_labels)


# Execute rendering
if __name__ == "__main__":
    # os.system(r"manim -qk -v WARNING -p --disable_caching -o PlayerCount.mp4 .\statsvideo\playercount.py PlayerCount")
    os.system(r"manim -qk -v WARNING -p --disable_caching -o MatchCount.png .\statsvideo\playercount.py MatchCount")