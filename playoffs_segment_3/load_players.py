import asyncio
from io import BytesIO
import json
import pandas as pd
from PIL import Image
import requests
from pathlib import Path

from rankedutils import api, constants


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
SEASON = 8


def get_player_data(nick, seed):
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
        "avg": round(season_data["completionTime"]["ranked"] / season_data["completions"]["ranked"]),
        "seed": seed
    }
    return stats


def save_head(nick, uuid):
    image = requests.get(f"https://mc-heads.net/avatar/{uuid}").content
    image = Image.open(BytesIO(image))
    image.save(ASSETS_DIR / f"{nick}.png")


async def save_versus(nicks):
    wr_df = pd.DataFrame(columns=nicks, index=nicks)
    wins_df = pd.DataFrame(columns=nicks, index=nicks)
    for i, player_1 in enumerate(nicks):
        print(player_1)
        for player_2 in nicks[i+1:]:
            wr, wins, losses = await process_versus(player_1, player_2)
            wr_df.at[player_1, player_2] = wr
            wins_df.at[player_1, player_2] = wins
            wr_df.at[player_2, player_1] = -wr if wr is not None else None
            wins_df.at[player_2, player_1] = losses

    wr_df.to_csv(DATA_DIR / "winrate.csv")
    wins_df.to_csv(DATA_DIR / "wins.csv")


async def process_versus(player_1, player_2):
    if player_1 == player_2:
        return None, None

    wins = 0
    losses = 0
    for season in range(7, 10):
        response_data = await api.Versus(player_1, player_2, season=season).get_async()
        uuid_1 = next(player["uuid"] for player in response_data["players"] if player_1 == player["nickname"])
        uuid_2 = next(player["uuid"] for player in response_data["players"] if player_2 == player["nickname"])
        wins += response_data["results"]["ranked"][uuid_1]
        losses += response_data["results"]["ranked"][uuid_2]
    if wins + losses == 0:
        winrate = None
    else:
        print((wins - losses), (wins + losses), (wins - losses) / (wins + losses))
        winrate = int(((wins - losses) / (wins + losses)) * 100)
    return winrate, wins, losses


async def main():
    nicks = ["lowk3y_", "doogile", "Infume", "bing_pigs", "hackingnoises", "DARVY__X1", "Aquacorde", "v_strid"]
    all_nicks = ["lowk3y_", "doogile", "Infume", "bing_pigs", "hackingnoises", "DARVY__X1", "Aquacorde", "v_strid", "edcr", "Ranik_", "7rowl", "silverrruns", "Feinberg", "BeefSalad", "KenanKardes", "TUDORULE"]
    seeds = [7, 3, 2, 6, 16, 12, 9, 14, 1, 8, 4, 5, 11, 10, 13, 15]
    player_data = {}
    for i, nick in enumerate(nicks):
        player_data[nick] = get_player_data(nick, seeds[i])
        save_head(nick, player_data[nick]["uuid"])
    all_player_data = {}
    for i, nick in enumerate(all_nicks):
        all_player_data[nick] = get_player_data(nick, seeds[i])
        save_head(nick, all_player_data[nick]["uuid"])

    await save_versus(nicks)

    with open(DATA_DIR / "players.json", "w") as f:
        json.dump(player_data, f, indent=4)

    with open(DATA_DIR / "all_players.json", "w") as f:
        json.dump(all_player_data, f, indent=4)

if __name__ == '__main__':
    asyncio.run(main())
