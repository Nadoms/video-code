from manim import *
import math
import pandas as pd
import os


COMMAND_COLOURS = {
    "card": "#003b5c",
    "plot": "#0057e5",
    "match": "#41b6e6",
    "analysis": "#3ea908",
    "race": "#f0cc2e",
    "help": "#ec894d",
    "background": "#e50000",
    "connect": "#e641b6",
    "disconnect": "#000066",
}
COMMANDS = [
    "card",
    "plot",
    "match",
    "analysis",
    "race",
    # "help",
    # "background",
    # "connect",
    # "disconnect",
]


class BotPlot(Scene):

    def construct(self):
        data_file = os.path.join("random", "botplot", "data", "calls.csv")
        df = pd.read_csv(data_file)

        start_time = df.iloc[0]["timestamp"]
        end_time = df.iloc[-1]["timestamp"]
        delta_days = math.ceil((end_time - start_time) / 60 / 60 / 24)

        # Add the Axes
        ax = Axes(x_range=[0, delta_days, 10],
                  y_range=[0, 50, 5],
                  tips=True,
                  axis_config={"include_numbers": True, "font_size": 20}
        )
        labels = ax.get_axis_labels(
            Tex("Days").scale(0.5),
            Tex("Successful Calls").scale(0.5)
        )
        self.add(ax, labels)

        command_data = {
            "card": [0] * delta_days,
            "plot": [0] * delta_days,
            "match": [0] * delta_days,
            "analysis": [0] * delta_days,
            "race": [0] * delta_days,
            "help": [0] * delta_days,
            "background": [0] * delta_days,
            "connect": [0] * delta_days,
            "disconnect": [0] * delta_days,
        }

        day = 0
        for command, caller, callee, timestamp, hidden, completed in df.values:
            if not completed:
                continue
            day = math.floor((timestamp - start_time) / 60 / 60 / 24)
            command_data[command][day] += 1


        for i, command in enumerate(COMMANDS):
            command_data[command]
            colour = ManimColor.from_hex(COMMAND_COLOURS[command], 1.0)
            line_graph = ax.plot_line_graph(
                range(0, delta_days),
                command_data[command],
                line_color=colour,
                add_vertex_dots=True,
                vertex_dot_radius=0.015
            )
            self.add(line_graph)
            square = Square(
                side_length=0.3,
                fill_color=colour,
                fill_opacity=1
            )
            square.to_edge(UP + RIGHT)
            square.shift(DOWN * 0.5 * i)
            self.add(square)
            label = Text(command, font_size=24, color=colour).next_to(square, LEFT, buff=0.5)
            self.add(label)


# Execute rendering
if __name__ == "__main__":
    os.system(r"manim -qk -v WARNING -p --disable_caching -r 1920,1080 -o BotPlot.png .\random\botplot\botplot.py BotPlot")