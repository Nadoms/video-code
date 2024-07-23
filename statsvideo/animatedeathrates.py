from manim import *
import pandas as pd
import os


class DeathThreeD(ThreeDScene):

    def construct(self):
        data_file = os.path.join("statsvideo", "data", "deathrates.csv")
        df = pd.read_csv(data_file)
        
        # Add the Axes
        ax = ThreeDAxes(
            x_range=[0, 7, 1],
            y_range=[0, 8, 1],
            z_range=[0, 8, 1],
            x_length=7,
            y_length=8,
            z_length=8
        )

        labels = ax.get_axis_labels(
            Tex("Rank").scale(0.5),
            Tex("Split").scale(0.5),
            Tex("Pace").scale(0.5)
        )

        self.add(ax, labels)

        ranks = ["Coal", "Iron", "Gold", "Emerald", "Diamond", "Netherite"]
        splits = ["Overworld", "Nether", "Bastion", "Fortress", "Blind", "Stronghold", "The End"]

        # Adding tick labels for x and y axes
        x_ticks = [Tex(rank).scale(0.4).rotate(0.5*PI).next_to(ax.c2p(x+1, 0, 0), DOWN) for x, rank in enumerate(ranks)]
        y_ticks = [Tex(split).scale(0.4).rotate(PI).next_to(ax.c2p(0, y+1, 0), LEFT) for y, split in enumerate(splits)]
        
        self.add(*x_ticks, *y_ticks)

        # Iterate through rows of the dataframe
        coal_bars = VGroup()
        bars = VGroup()
        z_scale = 8
        x = 0

        for index, row in df.iterrows():
            y = 0

            for z in row:
                y += 1

                bar = Prism(
                    dimensions=[0.5, 0.5, z * z_scale],
                    fill_color=ManimColor.from_rgb((int(x * 40), 50, int(y * 30)), 1.0),
                    fill_opacity=0.7
                )
                bar.shift(RIGHT * x + UP * y + OUT * z * z_scale / 2)
                if x == 0:
                    coal_bars.add(bar)
                else:
                    bars.add(bar)

            x += 1
        bars.shift(LEFT * 2.5 + DOWN * 4)
        coal_bars.shift(LEFT * 2.5 + DOWN * 4)
        # Add the bars to the scene

        # Set camera orientation
        self.set_camera_orientation(phi=60 * DEGREES, theta=-30 * DEGREES)
        self.wait(1)
        self.play(Write(coal_bars))
        self.wait(1)
        self.begin_ambient_camera_rotation(0.4)
        self.play(Write(bars))
        self.wait(8)
        self.stop_ambient_camera_rotation()


# Execute rendering
if __name__ == "__main__":
    os.system(r"manim -qk -v WARNING -p --disable_caching -o DeathThreeD.mp4 .\statsvideo\animatedeathrates.py DeathThreeD")