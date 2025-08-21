import asyncio
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
import numpy as np
from rankedutils import api, constants, insight


INCREMENT = 500
BATCH = 50
RANKS = {
    "coal": {
        1: 0,
        2: 400,
        3: 500,
    },
    "iron": {
        1: 600,
        2: 700,
        3: 800,
    },
    "gold": {
        1: 900,
        2: 1000,
        3: 1100,
    },
    "emerald": {
        1: 1200,
        2: 1300,
        3: 1400,
    },
    "diamond": {
        1: 1500,
        2: 1650,
        3: 1800,
    },
    "netherite": {
        1: 2000,
    },
}
eos = False
total_games = 0


def get_rank(elo):
    if not elo:
        return None
    last_rank = ""
    for rank in RANKS:
        for division in RANKS[rank]:
            if elo < RANKS[rank][division]:
                return last_rank
            last_rank = f"{rank} {division}"
    return last_rank


async def get_completion_sample(id, season):
    cut_matches = {}
    print(f"Fetching matches before {id} for season {season}")
    matches = await api.RecentMatches(before=id, season=season, type=2, count=100).get_async()
    for match in matches:
        global total_games
        total_games += 1
        if match["forfeited"] is True:
            match["result"]["time"] = None
        if match["id"] + INCREMENT > constants.FINAL_MATCHES[season] or id > constants.FINAL_MATCHES[season]:
            global eos
            eos = True
        winner_uuid = match["result"]["uuid"]
        winner_elo = next(
            (
                change["eloRate"]
                for change in match["changes"]
                if change["uuid"] == winner_uuid
            ), match["changes"][0]["eloRate"]
        )
        winner_rank = get_rank(winner_elo)
        cut_matches[match["id"]] = {
            "date": match["date"],
            "time": match["result"]["time"],
            "elo": winner_elo,
            "rank": winner_rank,
            "season": match["season"],
        }
    return cut_matches


async def find_completions():
    current_id = constants.FIRST_MATCHES[1]
    season = 1
    all_matches = {}
    reached_end = False
    while not reached_end:
        ids = range(current_id, current_id + BATCH * INCREMENT, INCREMENT)
        try:
            match_groups = await asyncio.gather(
                *[get_completion_sample(id, season) for id in ids]
            )
        except api.APIRateLimitError:
            print("got rate limited, awaiting...")
            await asyncio.sleep(610)
            continue

        for matches in match_groups:
            global eos
            if eos:
                season += 1
                current_id -= BATCH * INCREMENT
                eos = False
                if season > constants.SEASON:
                    reached_end = True
            all_matches.update(matches)
        current_id += BATCH * INCREMENT

    return sorted(list(all_matches.values()), key=lambda x: x["date"])


def analyse(all_matches):
    games = {
        f"season {season}": {
            f"{rank} {division}": len(
                [
                    match
                    for match in all_matches
                    if match["rank"] == f"{rank} {division}"
                    and match["season"] == season
                ]
            )
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    completions = {
        f"season {season}": {
            f"{rank} {division}": len(
                [
                    match
                    for match in all_matches
                    if match["rank"] == f"{rank} {division}"
                    and match["season"] == season
                    and match["time"]
                ]
            )
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    avg_completion = {
        f"season {season}": {
            f"{rank} {division}": int(np.mean(
                [
                    match["time"]
                    for match in all_matches
                    if match["rank"] == f"{rank} {division}"
                    and match["season"] == season
                    and match["time"]
                ]
            )) if completions[f"season {season}"][f"{rank} {division}"] else None
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    med_completion = {
        f"season {season}": {
            f"{rank} {division}": int(np.median(
                [
                    match["time"]
                    for match in all_matches
                    if match["rank"] == f"{rank} {division}"
                    and match["season"] == season
                    and match["time"]
                ]
            )) if completions[f"season {season}"][f"{rank} {division}"] else None
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }

    with open(ROOT_DIR / "redlime" / "redlime.json", "w") as f:
        json.dump(
            {
                "games": games,
                "completions": completions,
                "mean_completion": avg_completion,
                "median_completion": med_completion,
            },
            f,
            indent=4
        )



def main():
    all_matches = asyncio.run(find_completions())
    analyse(all_matches)


if __name__ == "__main__":
    main()
