import asyncio
import json
import os
from manim import *
from pathlib import Path
from numpy import isnan
import pandas as pd
from rankedutils import api, games


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
ALL_NICKS = ["lowk3y_", "doogile", "Infume", "bing_pigs", "hackingnoises", "DARVY__X1", "Aquacorde", "v_strid", "edcr", "Ranik_", "L9_SOFTCATBOY69", "silverrruns", "Feinberg", "BeefSalad", "KenanKardes", "TUDORULE"]
PLAYOFF_MATCHES = [
    2901042,
    2901216,
    2901138,
    2892439,
    2892340,
    2892263,
    2951792,
    2951724,
    2951676,
    2951606,
    2891597,
    2891529,
    2891462,
    2891397,
    2891952,
    2891879,
    2891789,
    2951309,
    2951234,
    2951143,
    2892976,
    2892849,
    2892769,
    2952525,
    2952449,
    2952379,
    2902019,
    2901944,
    2901822,
    2901725,
    2900776,
    2900680,
    2900600,
    2902567,
    2902477,
    2902406,
    2902329,
    2952136,
    2952006,
    2952070,
]


async def analyse_deaths():
    all_death_data = {}
    for player in ALL_NICKS:
        print(player)
        game_count = 0
        death_count = 0
        player_response = api.User(player).get()
        _, matches = await games.get_detailed_matches(player_response, 8, 0, 10000)
        for match in matches:
            game_count += 1
            timeline = match["timelines"]
            if (
                "projectelo.timeline.death" in (event["type"] for event in timeline if event["uuid"] == player_response["uuid"])
                or "projectelo.timeline.reset" in (event["type"] for event in timeline if event["uuid"] == player_response["uuid"])
            ):
                death_count += 1
        death_data = {
            "games": game_count,
            "deaths": death_count,
            "death_rate": round(death_count / game_count * 100, 1),
        }
        all_death_data[player] = death_data

    return all_death_data


def analyse_playoff_deaths():
    run_count = 0
    death_count = 0
    for id in PLAYOFF_MATCHES:
        match = api.Match(id).get()
        run_count += 2
        timeline = match["timelines"]
        for event in timeline:
            uuid_seen = ""
            if event["type"] in ["projectelo.timeline.death", "projectelo.timeline.reset"] and event["uuid"] != uuid_seen:
                death_count += 1
                uuid_seen = event["uuid"]
        print(death_count, run_count)
    death_data = {
        "runs": run_count,
        "deaths": death_count,
        "death_rate": round(death_count / run_count * 100, 1),
    }
    return death_data


class Plot(Scene):

    def construct(self):
        self.camera.background_color = WHITE
        Line.set_default(color=BLACK)
        Text.set_default(font="Minecraft", color=BLACK)
        Tex.set_default(color=BLACK)

        title = Text("Playoffs Competitors - Death Rates", font_size=24)
        title.to_edge(UP, buff=0.5)

        subtitle = Text("Using Season 8 Data", font_size=18)
        subtitle.next_to(title, DOWN, buff=0.2)

        # data = asyncio.run(analyse_deaths())
        # with open(DATA_DIR / "death.json", "w") as f:
        #     json.dump(data, f, indent=4)
        with open(DATA_DIR / "death.json") as f:
            data = json.load(f)

        data = dict(sorted(data.items(), key=lambda x: x[1]["death_rate"]))
        avg = round(sum(data[player]["death_rate"] for player in data) / 16, 1)
        print(avg)
        print(analyse_playoff_deaths())

        profiles = Group()
        for i, name in enumerate(data):
            profile = Group()
            icon = ImageMobject(ASSETS_DIR / f"{name}.png")
            name_txt = Text(name, font_size=20).next_to(icon, DOWN, buff=0.1).scale(0.8)
            game_txt = Text(f"{data[name]['games']} games", font_size=20).scale(0.7).next_to(name_txt, DOWN, buff=0.1)
            death_txt = Text(f"{data[name]['deaths']} deaths", font_size=20).scale(0.7).next_to(game_txt, DOWN, buff=0.1)
            rate_txt = Text(f"{data[name]['death_rate']}%", font_size=20).next_to(death_txt, DOWN, buff=0.1)
            profile.add(icon, name_txt, game_txt, death_txt, rate_txt)
            profile.shift(RIGHT * (i % 8 - 3.5) * 1.6 + DOWN * (i // 8) * 2.5).scale(0.8)
            profiles.add(profile)

        profiles.shift(UP * 2)

        self.add(title, subtitle)
        self.add(profiles)


if __name__ == "__main__":
    name = os.path.basename(__file__)[:-3]
    os.system(rf"manim -qp -o {name} {name}.py {name.capitalize()}")
