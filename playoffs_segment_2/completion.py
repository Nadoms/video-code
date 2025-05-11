from math import isnan
from manim import *
import os
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
Y_MIN = 480
Y_MAX = 1560
Y_STEP = 120
X_MIN = 0
X_MAX = 771
X_STEP = X_MAX * 4
DAY = 60 * 60 * 24
RANK_COLOURS = {
    900: "#bdbdbd",
    1200: "#fad43d",
    1500: "#30e858",
    2000: "#37dcdd",
    3000: "#3e3a3e",
}
ANY_COLOURS = [YELLOW, PURPLE_C, BLUE_B, RED_D, GREEN_B]
season_ends = [
    datetime(year=2023, month=6, day=15, hour=0),
    datetime(year=2023, month=9, day=19, hour=0),
    datetime(year=2024, month=1, day=6, hour=0),
    datetime(year=2024, month=4, day=21, hour=0),
    datetime(year=2024, month=8, day=21, hour=0),
    datetime(year=2024, month=12, day=21, hour=0),
    datetime(year=2025, month=4, day=21, hour=0),
]
season_end_days = None
other_interests = {
    "Overworld type buffs": datetime(year=2024, month=2, day=13, hour=0),
    "Seed distribution changes": datetime(year=2024, month=12, day=21, hour=0),
    "Seed filter buffs": datetime(year=2025, month=2, day=12, hour=0),
}


def compute_moving_average(data_points, window_size=30, step=5):
    data_points.sort(key=lambda x: x[0])
    start = int(data_points[0][0] + window_size / 2)
    end = int(data_points[-1][0] - window_size / 2)
    smoothed_dates = []
    smoothed_times = []
    smoothed_date = []
    smoothed_time = []
    nan_streak = False

    for date in range(start, end, step):
        lower_bound = date - window_size / 2
        upper_bound = date + window_size / 2

        filtered_points = [point[1] for point in data_points if lower_bound <= point[0] <= upper_bound]
        average_time = np.median(filtered_points)
        if not isnan(average_time):
            nan_streak = False
            smoothed_date.append(date)
            smoothed_time.append(average_time / 1000)
            for season_end in season_end_days:
                if lower_bound < season_end < upper_bound:
                    print(f"Season end: {season_end} ({date}), {average_time / 1000}")
        elif not nan_streak:
            nan_streak = True
            smoothed_dates.append(smoothed_date)
            smoothed_times.append(smoothed_time)
            smoothed_date = []
            smoothed_time = []
    smoothed_dates.append(smoothed_date)
    smoothed_times.append(smoothed_time)

    return smoothed_dates, smoothed_times


def format_time(raw_time):
    time = str(timedelta(seconds=raw_time))[2:7]
    if time[0] == "0":
        time = time[1:]
    return time


class Plot(Scene):

    def construct(self):
        # Data
        data_file = DATA_DIR / "completions.csv"
        data_points = pd.read_csv(data_file).values.tolist()
        first_match = data_points[0][0]
        global season_end_days
        season_end_days = [
            round((season_end.timestamp() - first_match) / 60 / 60 / 24, 3) for season_end in season_ends
        ]
        data_points = [
            (
                round((data[0] - first_match) / 60 / 60 / 24, 3),
                data[1],
                data[2],
                data[3],
                data[4]
            )
            for i, data in enumerate(data_points)
            if data[1] > 360000
            and i % 1 == 0
        ]

        # Title
        Text.set_default(font="Minecraft")
        title = Text("Completion Times Throughout Ranked History", font_size=24)
        title.move_to(ORIGIN).shift(UP * 2.3)
        # Subtitles
        rank_title = Text("By Rank", font_size=18)
        rank_title.next_to(title, DOWN, buff=0.1)
        bastion_title = Text("By Bastion Type", font_size=18)
        bastion_title.next_to(title, DOWN, buff=0.1)
        ow_title = Text("By Seed Type", font_size=18)
        ow_title.next_to(title, DOWN, buff=0.1)

        # Axes
        plane = NumberPlane(
            x_range=[X_MIN, X_MAX, X_STEP],
            y_range=[Y_MIN, Y_MAX, Y_STEP],
            axis_config={
                "include_numbers": False,
                "include_tip": False,
                "font_size": 16,
            },
            x_length=11,
            y_length=3.5,
            y_axis_config={
                "label_direction": LEFT,
            },
            x_axis_config={
                "label_direction": DOWN,
            },
            background_line_style={
                "stroke_color": GRAY,
                "stroke_width": 1,
            },
            faded_line_style={
                "stroke_color": DARK_GRAY,
                "stroke_width": 1,
            },
            faded_line_ratio=2,
        )

        def format_date(month, year):
            date = datetime(year=year, month=month, day=1)
            days_since = round((date.timestamp() - first_match) / 60 / 60 / 24, 3)
            return date.strftime("%b '%y"), days_since

        x_labels = VGroup()
        for x in range(2, 15):
            month, days_since = format_date(x * 2 % 12 + 1, 2023 + x * 2 // 12)
            label = Text(month).scale(0.2).next_to(
                plane.x_axis.n2p(days_since), DOWN, buff=0.2
            )
            x_labels.add(label)
        y_labels = VGroup()
        for y in range(Y_MIN, Y_MAX + 1, Y_STEP):
            label = Text(format_time(y)).scale(0.2).next_to(
                plane.y_axis.n2p(y), LEFT, buff=0.1
            )
            y_labels.add(label)

        # Axes labels
        labels = plane.get_axis_labels(
            Text("Month").scale(0.3),
            Text("Completion Time").scale(0.3)
        )

        # Dottage
        dots = VGroup()
        unranked_dots = VGroup()
        rank_dots = {
            900: VGroup(),
            1200: VGroup(),
            1500: VGroup(),
            2000: VGroup(),
            3000: VGroup(),
        }
        unbastion_dots = VGroup()
        bastion_dots = {
            "BRIDGE": VGroup(),
            "HOUSING": VGroup(),
            "STABLES": VGroup(),
            "TREASURE": VGroup(),
        }
        ow_dots = {
            "BURIED_TREASURE": VGroup(),
            "DESERT_TEMPLE": VGroup(),
            "RUINED_PORTAL": VGroup(),
            "SHIPWRECK": VGroup(),
            "VILLAGE": VGroup(),
        }
        for i, (date, time, elo, bastion, ow) in enumerate(data_points):
            time = time / 1000
            if not isnan(elo):
                colour_scale = min(max((elo - 600), 0) / 1500, 1)
            else:
                colour_scale = 0
            alpha_scale = max(min(1, ((1680 - time) / 240)), 0)
            colour = ManimColor.from_rgb((
                int((1 - colour_scale) * 255),
                int(50 + colour_scale * 100),
                int(colour_scale * 255)
            ), 1)

            dot = Dot(plane.c2p(date, time), color=colour, radius=0.010).set_opacity(alpha_scale)
            if i % 1000 == 0:
                print(i)
            dots.add(dot)
            if isnan(elo):
                unranked_dots.add(dot)
            else:
                for max_elo in rank_dots:
                    if elo < max_elo:
                        rank_dots[max_elo].add(dot)
                        break
            if bastion not in bastion_dots:
                unbastion_dots.add(dot)
            else:
                bastion_dots[bastion].add(dot)
            if ow in ow_dots:
                ow_dots[ow].add(dot)

        # Lineage
        rank_lines = {
            900: VGroup(),
            1200: VGroup(),
            1500: VGroup(),
            2000: VGroup(),
            3000: VGroup(),
        }
        bastion_lines = {
            "BRIDGE": VGroup(),
            "HOUSING": VGroup(),
            "STABLES": VGroup(),
            "TREASURE": VGroup(),
        }
        ow_lines = {
            "BURIED_TREASURE": VGroup(),
            "DESERT_TEMPLE": VGroup(),
            "RUINED_PORTAL": VGroup(),
            "SHIPWRECK": VGroup(),
            "VILLAGE": VGroup(),
        }

        min_elo = 0
        for i, max_elo in enumerate(rank_lines):
            smoothed_date, smoothed_time = compute_moving_average(
                [
                    (data[0], data[1])
                    for data in data_points
                    if not isnan(data[2]) and min_elo <= int(data[2]) < max_elo
                ]
            )
            colour = ManimColor.from_hex(RANK_COLOURS[max_elo])
            for j in range(len(smoothed_date)):
                if max_elo == 3000:
                    rank_lines[max_elo].add(plane.plot_line_graph(
                        x_values=smoothed_date[j],
                        y_values=smoothed_time[j],
                        stroke_width=4,
                        add_vertex_dots=False,
                        line_color=ManimColor.from_hex(GOLD),
                    ))
                rank_lines[max_elo].add(plane.plot_line_graph(
                    x_values=smoothed_date[j],
                    y_values=smoothed_time[j],
                    stroke_width=2,
                    add_vertex_dots=False,
                    line_color=colour,
                ))
            stroke_colour = WHITE
            text_colour = colour
            if max_elo == 3000:
                stroke_colour = ManimColor.from_hex(GOLD)
                text_colour = ManimColor.from_hex(GOLD)
            square = Square(
                side_length=0.2,
                fill_color=colour,
                fill_opacity=1,
                stroke_color=stroke_colour,
            ).to_edge(UP + RIGHT).shift(DOWN * 2.5 + 0.5 * RIGHT * 0.5 + DOWN * 0.4 * i)
            rank_lines[max_elo].add(square)
            legend_str = "2000+ Elo" if max_elo == 3000 else f"{min_elo}-{max_elo} Elo"
            legend = Text(legend_str, font_size=10, color=text_colour).next_to(square, LEFT, buff=0.1)
            rank_lines[max_elo].add(legend)
            min_elo = max_elo

        for i, bastion in enumerate(bastion_lines):
            smoothed_date, smoothed_time = compute_moving_average(
                [(data[0], data[1]) for data in data_points if data[3] == bastion]
            )
            colour = ManimColor.from_hex(ANY_COLOURS[i])
            for j in range(len(smoothed_date)):
                bastion_lines[bastion].add(plane.plot_line_graph(
                    x_values=smoothed_date[j],
                    y_values=smoothed_time[j],
                    stroke_width=2,
                    add_vertex_dots=False,
                    line_color=colour,
                ))
            square = Square(
                side_length=0.2,
                fill_color=colour,
                fill_opacity=1
            ).to_edge(UP + RIGHT).shift(DOWN * 2.5 + 0.5 * RIGHT * 0.5 + DOWN * 0.4 * i)
            bastion_lines[bastion].add(square)
            legend = Text(bastion.capitalize(), font_size=10, color=colour).next_to(square, LEFT, buff=0.2)
            bastion_lines[bastion].add(legend)

        for i, ow in enumerate(ow_lines):
            smoothed_date, smoothed_time = compute_moving_average(
                [(data[0], data[1]) for data in data_points if data[4] == ow]
            )
            colour = ManimColor.from_hex(ANY_COLOURS[i])
            for j in range(len(smoothed_date)):
                ow_lines[ow].add(plane.plot_line_graph(
                    x_values=smoothed_date[j],
                    y_values=smoothed_time[j],
                    stroke_width=2,
                    add_vertex_dots=False,
                    line_color=colour,
                ))
            square = Square(
                side_length=0.2,
                fill_color=colour,
                fill_opacity=1
            ).to_edge(UP + RIGHT).shift(DOWN * 2.5 + 0.5 * RIGHT * 0.5 + DOWN * 0.4 * i)
            ow_lines[ow].add(square)
            legend = Text(ow.capitalize(), font_size=10, color=colour).next_to(square, LEFT, buff=0.2)
            ow_lines[ow].add(legend)

        smoothed_date, smoothed_time = compute_moving_average(
            [(data[0], data[1]) for data in data_points]
        )
        line = plane.plot_line_graph(
            x_values=smoothed_date[0],
            y_values=smoothed_time[0],
            stroke_width=2,
            add_vertex_dots=False,
            line_color=WHITE,
        )

        season_markers = VGroup()
        other_markers = VGroup()
        for i, season_end in enumerate(season_ends):
            season_end_time = round((season_end.timestamp() - first_match) / 60 / 60 / 24, 3)
            marker = DashedLine(
                start=plane.c2p(season_end_time, Y_MIN),
                end=plane.c2p(season_end_time, 1440),
                stroke_width=2,
                color=YELLOW,
            )
            season_markers.add(marker)
            label = Text(f"S{i + 1} End", font_size=12).next_to(marker, UP, buff=0.1)
            season_markers.add(label)
        y = 1320
        for other_interest in other_interests:
            other_interest_time = round((other_interests[other_interest].timestamp() - first_match) / 60 / 60 / 24, 3)
            marker = Line(
                start=plane.c2p(other_interest_time, Y_MIN),
                end=plane.c2p(other_interest_time, y),
                stroke_width=4,
                color=BLUE_B,
            )
            other_markers.add(marker)
            label = Text(other_interest, font_size=9).next_to(marker, UP, buff=0.1)
            other_markers.add(label)
            y -= 60

        # Animation
        self.play(Write(title), Write(plane))
        self.play(Write(labels), Write(x_labels), Write(y_labels))
        self.wait()
        self.play(Write(dots), run_time=1)
        self.wait()
        for marker in season_markers:
            self.play(Write(marker), run_time=0.5)
        self.wait()
        self.play(Write(line), run_time=3)
        self.wait()
        self.play(FadeOut(dots))
        self.wait()
        self.play(Unwrite(line), Write(rank_title))
        for max_elo in rank_lines:
            self.play(Write(rank_lines[max_elo]), run_time=2)
        self.wait()
        self.play(*[Unwrite(rank_lines[max_elo]) for max_elo in rank_lines], Unwrite(season_markers), Unwrite(rank_title))
        self.play(*[Write(ow_lines[ow], run_time=3) for ow in ow_lines], Write(ow_title))
        self.wait()
        for marker in other_markers:
            self.play(Write(marker), run_time=0.5)
        self.wait()
        # self.play(*[Unwrite(ow_lines[ow]) for ow in ow_lines], Unwrite(ow_title))
        # self.play(*[Write(bastion_lines[bastion], run_time=3) for bastion in bastion_lines], Write(bastion_title))


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qk -v WARNING -p --disable_caching -r 2880,1080 -o {name}.mp4 {name}.py {name.capitalize()}")
