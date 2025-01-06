from io import BytesIO
import json
import pandas as pd
from PIL import Image
import requests
from pathlib import Path


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"


def get_player_data(nick):
    response_data = requests.get(f"https://mcsrranked.com/api/users/{nick}?season=6").json()["data"]
    season_data = response_data["statistics"]["season"]
    stats = {
        "games": season_data["playedMatches"]["ranked"],
        "playtime": season_data["playtime"]["ranked"],
        "elo": response_data["seasonResult"]["last"]["eloRate"],
        "avg": round(season_data["completionTime"]["ranked"] / season_data["completions"]["ranked"])
    }
    return stats


def save_head(nick):
    image = requests.get(f"https://mc-heads.net/avatar/{nick}").content
    image = Image.open(BytesIO(image))
    image.save(ASSETS_DIR / f"{nick}.png")


def save_versus(nicks):
    wr_df = pd.DataFrame(columns=nicks, index=nicks)
    wins_df = pd.DataFrame(columns=nicks, index=nicks)
    for player_1 in nicks:
        for player_2 in nicks:
            wr, wins = process_versus(player_1, player_2)
            wr_df.at[player_2, player_1] = wr
            wins_df.at[player_2, player_1] = wins

    wr_df.to_csv(DATA_DIR / "winrate.csv")
    wins_df.to_csv(DATA_DIR / "wins.csv")


def process_versus(player_1, player_2):
    if player_1 == player_2:
        return None, None

    response_data = requests.get(f"https://mcsrranked.com/api/users/{player_1}/versus/{player_2}?season=6").json()["data"]
    for player in response_data["players"]:
        if player_1 == player["nickname"]:
            uuid_1 = player["uuid"]
        else:
            uuid_2 = player["uuid"]
    wins = response_data["results"]["ranked"][uuid_1]
    losses = response_data["results"]["ranked"][uuid_2]
    if wins + losses == 0:
        winrate = None
    else:
        winrate = round(wins / (wins + losses), 3)
    return winrate, wins


def main():
    response_data = requests.get("https://mcsrranked.com/api/phase-leaderboard?season=6").json()["data"]
    top_nicks = [player["nickname"] for player in response_data["users"][:12]]
    extras = ["ELO_PLUMBER4444", "TUDORULE", "Erikfzf", "dandannyboy"]
    nicks = top_nicks + extras
    player_data = {}

    for nick in nicks:
        save_head(nick)
        player_data[nick] = get_player_data(nick)

    save_versus(nicks)

    with open(DATA_DIR / "players.json", "w") as f:
        json.dump(player_data, f, indent=4)

if __name__ == '__main__':
    main()
