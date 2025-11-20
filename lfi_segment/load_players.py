import asyncio
from io import BytesIO
import json
import pandas as pd
from PIL import Image
import requests
from pathlib import Path

from rankedutils import api, constants, games, insight


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
SEASON = 9
PLAYERS = [
    "v_strid",
    "Kxpow",
    "NOHACKSJUSTTIGER",
    "BeefSalad",
    "silverrruns",
    "bing_pigs",
    "hackingnoises",
    "7rowl"
]


def get_player_data(nick):
    response_data = api.User(nick, season=SEASON).get()
    season_data = response_data["statistics"]["season"]
    stats = {
        "uuid": response_data["uuid"],
        "games": season_data["playedMatches"]["ranked"],
        "completions": season_data["completions"]["ranked"],
        "win_loss": season_data["wins"]["ranked"] / season_data["loses"]["ranked"],
        "sb": season_data["bestTime"]["ranked"],
        "playtime": season_data["playtime"]["ranked"],
        "peak_elo": response_data["seasonResult"]["highest"],
        "elo": response_data["seasonResult"]["last"]["eloRate"],
        "avg": round(season_data["completionTime"]["ranked"] / season_data["completions"]["ranked"])
    }
    return stats


def save_head(nick, uuid):
    image = requests.get(f"https://mc-heads.net/avatar/{uuid}").content
    image = Image.open(BytesIO(image))
    image.save(ASSETS_DIR / f"{nick}.png")


def get_history(uuid):
    elo_history = []
    completion_history = []
    matches = games.get_matches(uuid, 9, False)
    for match in matches:
        elo = insight.get_match_elo(uuid, match)
        completion = insight.get_match_completion(uuid, match)
        elo_history.append((elo, match["date"]))
        if completion is not None:
            completion_history.append(completion)

    return list(reversed(elo_history)), list(reversed(completion_history))


async def main():
    player_data = {}
    elo_histories = {}
    completion_histories = {}
    for i, nick in enumerate(PLAYERS):
        player_data[nick] = get_player_data(nick)
        elo_histories[nick], completion_histories[nick] = get_history(player_data[nick]["uuid"])
        save_head(nick, player_data[nick]["uuid"])

    with open(DATA_DIR / "players.json", "w") as f:
        json.dump(player_data, f, indent=4)
    with open(DATA_DIR / "elo_history.json", "w") as f:
        json.dump(elo_histories, f, indent=4)
    with open(DATA_DIR / "comp_history.json", "w") as f:
        json.dump(completion_histories, f, indent=4)

if __name__ == '__main__':
    asyncio.run(main())
