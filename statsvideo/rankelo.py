from manim import *
import pandas as pd
import os

class RankElo(Scene):

    def construct(self):
        data_file = os.path.join("statsvideo", "data", "rankelo.csv")
        df = pd.read_csv(data_file)

        players = [4659, 3795, 2583, 3410, 3678, 2907]
        seasons = ["S1", "S2", "S3", "S4", "S5", "S6"]

        # Animate the creation of Axes
        ax = Axes(x_range=[0, 100, 10],
                  y_range=[0, 2400, 200],
                  x_length=10,
                  y_length=14,
                  tips=True,
                  axis_config={"include_numbers": True, "font_size": 20}
        )
        
        # Create the grid
        grid = NumberPlane(
            x_range=[0, 100, 10],
            y_range=[0, 2400, 200],
            x_length=10,
            y_length=14,
            axis_config={"include_numbers": False},
            background_line_style={"stroke_opacity": 0.2}
        )

        labels = ax.get_axis_labels(
            Tex("Percentile").scale(0.5),
            Tex("Elo").scale(0.5)
        )

        dots = VGroup()
        dot_colours = ["#003f5c", "#58508d", "#bc5090", "#ff6361", "#ffa600", "#ffe080"]

        for rank, season_elos in enumerate(df.values):
            for i, elo in enumerate(season_elos[1:]):
                if elo:
                    percentile = rank / players[i] * 100
                    colour = dot_colours[i]
                    dot = Dot(ax.c2p(percentile, elo), color=colour, radius=0.015)
                    dots.add(dot)

        legend_items = [Dot(color=color).scale(0.5).next_to(Tex(season).scale(0.5), RIGHT) 
                        for color, season in zip(dot_colours, seasons)]
        legend = VGroup(*[VGroup(item, Tex(season).scale(0.5)).arrange(RIGHT, buff=0.1) 
                          for item, season in zip(legend_items, seasons)])
        legend.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.to_corner(UL)

        group = VGroup(ax, grid, labels, *dots, legend)

        self.add(group)


# Execute rendering
if __name__ == "__main__":
    os.system(r"manim -qk -v WARNING -p --disable_caching -r 1080,1260 -o RankElo.png .\statsvideo\rankelo.py RankElo")