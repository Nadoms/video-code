import math
import sys
from dotenv import load_dotenv
from io import BytesIO
import json
from os import getenv
import pandas as pd
from PIL import Image
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
import api


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
SEASON_START = 1734739200
SEASON_END = 1745194600
DAY = 86400
SEASON_LENGTH = (SEASON_END - SEASON_START) // DAY
SEASON = 7


def get_player_data(nick):
    response_data = api.User(nick, season=7).get()
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


def save_history(nicks, full=False):
    history_df = pd.DataFrame(columns=nicks)
    for nick in nicks:
        print(f"Checking {nick}'s history")
        if full:
            mega_history = []
            for s in reversed(range(1, SEASON + 1)):
                print(f"season {s}")
                mega_history += get_history(nick, s, len(mega_history))
            print(mega_history)
        else:
            mega_history = get_history(nick)
        history_df[nick] = pd.Series(reversed(mega_history))

    history_df.to_csv(DATA_DIR / f"history_{full}.csv")


def get_history(nick, season=7, start_day=0):
    i = 0
    last_day = -1
    day = -1
    history = []
    response_data = None
    uuid = api.User(nick, season=season).get()["uuid"]

    last_id = 10000000
    while True:
        response_data = api.UserMatches(nick, before=last_id, season=season, type=2, excludedecay=False).get()
        if response_data == []:
            for _ in range(SEASON_LENGTH - len(history)):
                history.append(None)
            break
        last_id = response_data[-1]["id"]

        for match in response_data:
            assert match["date"] <= SEASON_END
            day = (SEASON_END - match["date"]) // DAY

            if day != last_day:
                if day - last_day >= 1:
                    for _ in range(day - last_day - 1):
                        history.append(None)
                try:
                    if match["changes"][0]["uuid"] == uuid:
                        elo = match["changes"][0]["eloRate"] + match["changes"][0]["change"]
                    else:
                        elo = match["changes"][1]["eloRate"] + match["changes"][1]["change"]
                    history.append(elo)
                    assert len(history) == day - start_day
                    last_day = day
                except:
                    last_day = day
        i += 1
        print(f"day {day}")

    last_elo = None
    for i in reversed(range(len(history))):
        if history[i] is None:
            history[i] = last_elo
        last_elo = history[i]

    return history


def main():
    response_data = requests.get(
        f"{API_URL}/phase-leaderboard?season=7",
        headers=HEADERS,
    ).json()["data"]
    top_nicks = [player["nickname"] for player in response_data["users"][:16]]
    extras = ["ELO_PLUMBER4444", "TUDORULE", "Erikfzf", "dandannyboy"]
    nicks = top_nicks #  + extras
    player_data = {}
    for nick in nicks:
        player_data[nick] = get_player_data(nick)
        save_head(nick, player_data[nick]["uuid"])

    # save_versus(nicks)
    save_history(nicks, False)

    with open(DATA_DIR / "players.json", "w") as f:
        json.dump(player_data, f, indent=4)

if __name__ == '__main__':
    main()
