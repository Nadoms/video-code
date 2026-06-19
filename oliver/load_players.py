import asyncio
from io import BytesIO
import json
import pandas as pd
import requests
from pathlib import Path
from datetime import datetime, time, timedelta

from rankedutils import api, constants, numb, games


ROOT = Path(__file__).parent
ASSETS_DIR = ROOT / "assets"
DATA_DIR = ROOT / "data"
SEASON = 10


def get_seed_stats(uuid, matches):
    seed_stats = {
        "ow": {ow: {
            "wins": 0,
            "losses": 0,
            "winrate": 0,
            "total_completion_time": 0,
            "completions": 0,
            "avg": 0,
            "avg_legible": ""
        } for ow in constants.OVERWORLDS},
        "bastion": {bastion: {
            "wins": 0,
            "losses": 0,
            "winrate": 0,
            "total_completion_time": 0,
            "completions": 0,
            "avg": 0,
            "avg_legible": ""
        } for bastion in constants.BASTIONS}
    }

    for match in matches:
        ow = match["seedType"]
        bastion = match["bastionType"]
        if uuid == match["result"]["uuid"]:
            seed_stats["ow"][ow]["wins"] += 1
            seed_stats["bastion"][bastion]["wins"] += 1
            if not match["forfeited"]:
                seed_stats["ow"][ow]["total_completion_time"] += match["result"]["time"]
                seed_stats["ow"][ow]["completions"] += 1
                seed_stats["bastion"][bastion]["total_completion_time"] += match["result"]["time"]
                seed_stats["bastion"][bastion]["completions"] += 1
        elif match["result"]["uuid"] is not None:
            seed_stats["ow"][ow]["losses"] += 1
            seed_stats["bastion"][bastion]["losses"] += 1

    for ow in constants.OVERWORLDS:
        if seed_stats["ow"][ow]["wins"] + seed_stats["ow"][ow]["losses"] > 0:
            seed_stats["ow"][ow]["winrate"] = round(seed_stats["ow"][ow]["wins"] / (seed_stats["ow"][ow]["wins"] + seed_stats["ow"][ow]["losses"]), 3)
        if seed_stats["ow"][ow]["completions"] > 0:
            seed_stats["ow"][ow]["avg"] = round(seed_stats["ow"][ow]["total_completion_time"] / seed_stats["ow"][ow]["completions"])
            seed_stats["ow"][ow]["avg_legible"] = numb.digital_time(seed_stats["ow"][ow]["avg"])
    for bastion in constants.BASTIONS:
        if seed_stats["bastion"][bastion]["wins"] + seed_stats["bastion"][bastion]["losses"] > 0:
            seed_stats["bastion"][bastion]["winrate"] = round(seed_stats["bastion"][bastion]["wins"] / (seed_stats["bastion"][bastion]["wins"] + seed_stats["bastion"][bastion]["losses"]), 3)
        if seed_stats["bastion"][bastion]["completions"] > 0:
            seed_stats["bastion"][bastion]["avg"] = round(seed_stats["bastion"][bastion]["total_completion_time"] / seed_stats["bastion"][bastion]["completions"])
            seed_stats["bastion"][bastion]["avg_legible"] = numb.digital_time(seed_stats["bastion"][bastion]["avg"])

    return seed_stats


async def get_player_data(nick):
    try:
        response_data = api.User(nick, season=SEASON).get()
    except api.APIRateLimitError:
        await asyncio.sleep(910)
        response_data = api.User(nick, season=SEASON).get()
    season_data = response_data["statistics"]["season"]

    try:
        _, matches = await games.get_detailed_matches(response_data, SEASON, 0, 10000)
    except api.APIRateLimitError:
        await asyncio.sleep(910)
        _, matches = await games.get_detailed_matches(response_data, SEASON, 0, 10000)
    stats = {
        "uuid": response_data["uuid"],
        "games": season_data["playedMatches"]["ranked"],
        "completions": season_data["completions"]["ranked"],
        "winrate": round(season_data["wins"]["ranked"] / (season_data["wins"]["ranked"] + season_data["loses"]["ranked"]), 3),
        "sb": season_data["bestTime"]["ranked"],
        "sb_legible": f"{numb.digital_time(season_data["bestTime"]["ranked"])}",
        "playtime": season_data["playtime"]["ranked"],
        "playtime_legible": f"{round(season_data["playtime"]["ranked"] / 1000 / 60 / 60)} hours",
        "peak_elo": response_data["seasonResult"]["highest"],
        "elo": response_data["seasonResult"]["last"]["eloRate"],
        "avg": round(season_data["completionTime"]["ranked"] / season_data["completions"]["ranked"]),
        "avg_legible": f"{numb.digital_time(round(season_data["completionTime"]["ranked"] / season_data["completions"]["ranked"]))}",
        "seed_stats": get_seed_stats(response_data["uuid"], matches)
    }
    return stats


async def save_versus(nicks):
    wr_df = pd.DataFrame(columns=nicks, index=nicks)
    wins_df = pd.DataFrame(columns=nicks, index=nicks)
    for i, player_1 in enumerate(nicks):
        print(player_1)
        for player_2 in nicks[i+1:]:
            wr, wins, losses = await process_versus(player_1, player_2)
            wr_df.at[player_1, player_2] = wr
            wins_df.at[player_1, player_2] = wins
            wr_df.at[player_2, player_1] = 100-wr if wr is not None else None
            wins_df.at[player_2, player_1] = losses

    wr_df.to_csv(DATA_DIR / "winrate.csv")
    wins_df.to_csv(DATA_DIR / "wins.csv")


async def process_versus(player_1, player_2):
    if player_1 == player_2:
        return None, None, None

    wins = 0
    losses = 0
    response_data = await api.Versus(player_1, player_2, season=10).get_async()
    uuid_1 = next(player["uuid"] for player in response_data["players"] if player_1 == player["nickname"])
    uuid_2 = next(player["uuid"] for player in response_data["players"] if player_2 == player["nickname"])
    wins += response_data["results"]["ranked"][uuid_1]
    losses += response_data["results"]["ranked"][uuid_2]
    if wins + losses == 0:
        winrate = None
    else:
        winrate = round(((wins) / (wins + losses)), 3)
        print(winrate, player_1, player_2, wins, losses)
    return winrate, wins, losses


async def main():
    nicks = ["Pinne", "doogile", "Infume", "bing_pigs", "hackingnoises", "Feinberg", "Aquacorde", "Ancoboyy", "pavkin", "MrBudgiee", "silverrruns", "HDMICables"]
    player_data = {}
    for i, nick in enumerate(nicks):
        print(nick)
        player_data[nick] = await get_player_data(nick)

    with open(DATA_DIR / "players.json", "w") as f:
        json.dump(player_data, f, indent=4)

    await save_versus(nicks)

if __name__ == '__main__':
    asyncio.run(main())
