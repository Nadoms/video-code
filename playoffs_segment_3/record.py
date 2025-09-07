import os
from manim import *
from pathlib import Path
from numpy import isnan
import pandas as pd


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"


class Plot(Scene):

    def construct(self):
        self.camera.background_color = WHITE
        Line.set_default(color=BLACK)
        Text.set_default(font="Minecraft", color=BLACK)
        wr_df = pd.read_csv(DATA_DIR / "winrate.csv", index_col=0)
        w_df = pd.read_csv(DATA_DIR / "wins.csv", index_col=0)
        wr_data = wr_df.values.tolist()
        w_data = w_df.values.tolist()
        row_labels = [Text("") for i in range(8)]
        col_labels = [Text("") for i in range(8)]
        mock_table_cells = [[f"Mi" for cell in winrates] for winrates in wr_data]
        icons = [ImageMobject(ASSETS_DIR / f"{name}.png").scale(0.45) for name in list(wr_df.index)]

        title = Text("Playoffs Competitors - Win-Loss Differential", font_size=24)
        title.to_edge(UP, buff=0.5)

        subtitle = Text("Using Season 7, 8 and 9 Data", font_size=18)
        subtitle.to_edge(DOWN, buff=0.5)

        table = Table(
            mock_table_cells,
            row_labels=row_labels,
            col_labels=col_labels,
            top_left_entry=Cross().scale(0.3),
            include_outer_lines=True,
            h_buff=0.7,
            v_buff=0.7,
        ).scale(0.5)

        icon_group = Group()
        for i, icon in enumerate(icons):
            cell = table.get_cell((1, i + 2))
            icon_copy = icon.copy()
            icon_copy.stretch_to_fit_width(cell.width)
            icon_copy.stretch_to_fit_height(cell.height)
            icon_copy.move_to(cell.get_center())
            icon_group.add(icon_copy)
        for i, icon in enumerate(icons):
            cell = table.get_cell((i + 2, 1))
            icon_copy = icon.copy()
            icon_copy.stretch_to_fit_width(cell.width)
            icon_copy.stretch_to_fit_height(cell.height)
            icon_copy.move_to(cell.get_center())
            icon_group.add(icon_copy)

        gradient = color_gradient(
            (
                ManimColor.from_rgb((255, 70, 70)),
                ManimColor.from_rgb((235, 70, 80)),
                ManimColor.from_rgb((159, 100, 159)),
                ManimColor.from_rgb((70, 127, 235)),
                ManimColor.from_rgb((70, 159, 255))
            ),
            101,
        )

        table_cells = VGroup()
        table_heat = VGroup()
        for i, winrates in enumerate(wr_data):
            for j, winrate in enumerate(winrates):
                colour = gradient[int((winrate + 100) / 2)] if not isnan(winrate) else GRAY_A
                radius = (w_data[i][j] + w_data[j][i]) ** 0.25 * 0.10

                cell = table.get_cell((i + 2, j + 2))
                cell_str = f"{int(winrate)}%" if not isnan(winrate) else "/"
                cell_text = Text(cell_str, font_size=16, fill_opacity=0.8).scale(0.5)
                cell_text.move_to(cell.get_center())
                table_cells.add(cell_text)

                heat = VGroup()
                rings = 32
                for k, r in enumerate(np.linspace(radius, 0, rings)):
                    heat.add(Circle(radius=r, color=colour, fill_opacity=k / rings / 2, stroke_width=0))
                heat.move_to(cell.get_center())
                table_heat.add(heat)

        example_heat = VGroup()
        for i, game_count in enumerate(reversed((1, 5, 25, 125))):
            radius = game_count ** 0.25 * 0.10
            heat = VGroup()
            rings = 32
            for k, r in enumerate(np.linspace(radius, 0, rings)):
                heat.add(Circle(radius=r, color=ManimColor.from_rgb((70, 159, 255)), fill_opacity=k / rings / 2, stroke_width=0))
            heat.shift(DOWN * (i - 1.5) / 1.5 + RIGHT * 5)
            example_heat.add(heat)

        self.add(icon_group)
        self.add(table.vertical_lines, table.horizontal_lines)
        self.add(title, subtitle)
        self.add(table_heat, example_heat)
        self.add(table_cells)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -p -o {name} {name}.py {name.capitalize()}")
