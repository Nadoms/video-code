import math
from dotenv import load_dotenv
from io import BytesIO
import json
from os import getenv
import pandas as pd
from PIL import Image
import requests
from pathlib import Path


load_dotenv()
ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
API_KEY = getenv("API_KEY")
API_URL = "https://mcsrranked.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:110.0) Gecko/20100101 Firefox/110.0.",
    "API-Key": API_KEY,
}
SEASON_START = 1724198400
DAY = 86400


def get_player_data(nick):
    response_data = requests.get(
        f"{API_URL}/users/{nick}?season=6",
        headers=HEADERS,
    ).json()["data"]
    season_data = response_data["statistics"]["season"]
    stats = {
        "uuid": response_data["uuid"],
        "games": season_data["playedMatches"]["ranked"],
        "playtime": season_data["playtime"]["ranked"],
        "elo": response_data["seasonResult"]["last"]["eloRate"],
        "avg": round(season_data["completionTime"]["ranked"] / season_data["completions"]["ranked"])
    }
    return stats


def save_head(nick, uuid):
    image = requests.get(f"https://mc-heads.net/avatar/{uuid}").content
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

    response_data = requests.get(
        f"{API_URL}/users/{player_1}/versus/{player_2}?season=6",
        headers=HEADERS,
    ).json()["data"]
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


def save_history(nicks):
    history_df = pd.DataFrame(columns=nicks)
    for nick in nicks:
        print(f"Checking {nick}'s history")
        history = get_history(nick)
        print(history)
        history_df[nick] = pd.Series(history)

    history_df.to_csv(DATA_DIR / "history.csv")


def get_history(nick):
    i = 0
    last_day = -1
    history = [None] * 122
    response_data = None
    uuid = requests.get(
        f"{API_URL}/users/{nick}?season=6",
        headers=HEADERS,
    ).json()["data"]["uuid"]

    while response_data != []:
        url = f"{API_URL}/users/{nick}/matches?page={i}&season=6&type=2&count=50"
        response_data = requests.get(
            url,
            headers=HEADERS,
        ).json()["data"]

        for match in response_data:
            assert match["date"] >= SEASON_START
            day = (match["date"] - SEASON_START) // DAY
            if day >= 122:
                print("Snapped", match["id"])
                day = 121

            if day != last_day:
                try:
                    if match["changes"][0]["uuid"] == uuid:
                        elo = match["changes"][0]["eloRate"] + match["changes"][0]["change"]
                    else:
                        elo = match["changes"][1]["eloRate"] + match["changes"][1]["change"]
                    history[day] = elo
                    last_day = day
                except:
                    last_day = day

        i += 1

    last_elo = -1
    for i in range(len(history)):
        if history[i] is None:
            history[i] = last_elo
        last_elo = history[i]

    return history


def main():
    response_data = requests.get(
        f"{API_URL}/phase-leaderboard?season=6",
        headers=HEADERS,
    ).json()["data"]
    top_nicks = [player["nickname"] for player in response_data["users"][:12]]
    extras = ["ELO_PLUMBER4444", "TUDORULE", "Erikfzf", "dandannyboy"]
    nicks = top_nicks + extras
    player_data = {}

    for nick in nicks:
        player_data[nick] = get_player_data(nick)
        save_head(nick, player_data[nick]["uuid"])

    # save_versus(nicks)
    save_history(nicks)

    with open(DATA_DIR / "players.json", "w") as f:
        json.dump(player_data, f, indent=4)

if __name__ == '__main__':
    main()
