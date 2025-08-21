import asyncio
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
import numpy as np
from rankedutils import api, constants, insight


INCREMENT = 1000
COUNT = 100
BATCH = 5
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
total_runs = 0


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


async def get_splits_sample(id, season):
    cut_runs = {}
    print(f"Fetching matches before {id} for season {season}")
    matches_simple = await api.RecentMatches(before=id, season=season, type=2, count=COUNT).get_async()
    matches = await asyncio.gather(
        *[api.Match(match_simple["id"]).get_async() for match_simple in matches_simple]
    )
    api.Match.commit()
    for match in matches:
        split_times = insight.get_splits_naive(match)
        for i, player in enumerate(match["players"]):
            global total_runs
            total_runs += 1
            if match["id"] + INCREMENT > constants.FINAL_MATCHES[season] or id > constants.FINAL_MATCHES[season]:
                global eos
                eos = True
            uuid = player["uuid"]
            elo = next(
                (
                    change["eloRate"]
                    for change in match["changes"]
                    if change["uuid"] == uuid
                ), match["changes"][0]["eloRate"]
            )
            rank = get_rank(elo)
            cut_runs[f"{match['id']}{chr(ord('a') + i)}"] = {
                "date": match["date"],
                "time": match["result"]["time"] if match["forfeited"] is False else None,
                "elo": elo,
                "rank": rank,
                "season": match["season"],
                "splits": split_times[uuid]
            }
    return cut_runs


async def find_completions():
    season = 5
    current_id = constants.FIRST_MATCHES[season] + COUNT
    all_runs = {}
    reached_end = False
    while not reached_end:
        ids = range(current_id, current_id + BATCH * INCREMENT, INCREMENT)
        try:
            run_groups = await asyncio.gather(
                *[get_splits_sample(id, season) for id in ids]
            )
        except api.APIRateLimitError:
            print("got rate limited, awaiting...")
            await asyncio.sleep(610)
            continue
        except:
            print("other error continueing", ids)

        for runs in run_groups:
            global eos
            if eos:
                season += 1
                current_id -= BATCH * INCREMENT
                eos = False
                if season > constants.SEASON:
                    reached_end = True
            all_runs.update(runs)
        current_id += BATCH * INCREMENT

    print(json.dumps(all_runs, indent=4))
    return sorted(list(all_runs.values()), key=lambda x: x["date"])


def analyse(all_runs):
    games = {
        f"season {season}": {
            f"{rank} {division}": len(
                [
                    run
                    for run in all_runs
                    if run["rank"] == f"{rank} {division}"
                    and run["season"] == season
                ]
            )
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    completions = {
        f"season {season}": {
            f"{rank} {division}": len(
                [
                    run
                    for run in all_runs
                    if run["rank"] == f"{rank} {division}"
                    and run["season"] == season
                    and run["time"]
                ]
            )
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    avg_completion = {
        f"season {season}": {
            f"{rank} {division}": int(np.mean(
                [
                    run["time"]
                    for run in all_runs
                    if run["rank"] == f"{rank} {division}"
                    and run["season"] == season
                    and run["time"]
                ]
            )) if completions[f"season {season}"][f"{rank} {division}"] else None
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    med_completion = {
        f"season {season}": {
            f"{rank} {division}": int(np.median(
                [
                    run["time"]
                    for run in all_runs
                    if run["rank"] == f"{rank} {division}"
                    and run["season"] == season
                    and run["time"]
                ]
            )) if completions[f"season {season}"][f"{rank} {division}"] else None
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    split_completed = {
        f"season {season}": {
            f"{rank} {division}": {
                split: len(
                    [
                        run["splits"][split]
                        for run in all_runs
                        if run["rank"] == f"{rank} {division}"
                        and run["season"] == season
                        and run["splits"][split]
                    ]
                )
                for split in constants.SPLITS
            }
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    avg_split = {
        f"season {season}": {
            f"{rank} {division}": {
                split: int(np.mean(
                    [
                        run["splits"][split]
                        for run in all_runs
                        if run["rank"] == f"{rank} {division}"
                        and run["season"] == season
                        and run["splits"][split]
                    ]
                )) if split_completed[f"season {season}"][f"{rank} {division}"][split] else None
                for split in constants.SPLITS
            }
            for rank in RANKS for division in RANKS[rank]
        } for season in range(1, constants.SEASON + 1)
    }
    med_split = {
        f"season {season}": {
            f"{rank} {division}": {
                split: int(np.median(
                    [
                        run["splits"][split]
                        for run in all_runs
                        if run["rank"] == f"{rank} {division}"
                        and run["season"] == season
                        and run["splits"][split]
                    ]
                )) if split_completed[f"season {season}"][f"{rank} {division}"][split] else None
                for split in constants.SPLITS
            }
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
                "split_completed": split_completed,
                "mean_split": avg_split,
                "median_split": med_split,
            },
            f,
            indent=4
        )



def main():
    all_runs = asyncio.run(find_completions())
    analyse(all_runs)


if __name__ == "__main__":
    main()
