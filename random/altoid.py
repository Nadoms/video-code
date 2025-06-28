from datetime import timedelta
import json
import numpy as np
import requests

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
import db


API_URL = "https://mcsrranked.com/api"

PB_SPLITS = {
    "story.enter_the_nether": 90791,
    "nether.find_bastion": 106197,
    "nether.find_fortress": 242145,
    "projectelo.timeline.blind_travel": 308734,
    "story.follow_ender_eye": 370861,
    "story.enter_the_end": 389095,
    "completion": 441909,
}


def combine_lbs():
    # https://docs.mcsrranked.com/#record-leaderboard
    all_runs = []
    all_ids = set()
    full_lb = requests.get(f"{API_URL}/record-leaderboard").json()["data"]

    # Get the match IDs from the lifetime leaderboard
    for match in full_lb:
        # Don't bother with longer runs
        if match["time"] < 450000:
            all_ids.add(match["id"])
    # Get any extra matches from season leaderboards
    # Doing both bc lowk3y is missing off these and prob ranik too etc
    for season in range(1, 9):
        lb = requests.get(f"{API_URL}/record-leaderboard?season={season}").json()["data"]
        for match in lb:
            if match["time"] < 450000:
                all_ids.add(match["id"])

    print("Fetched leaderboards")

    # Get info about each match using https://docs.mcsrranked.com/#matches-matchid
    for match_id in all_ids:
        match = requests.get(f"{API_URL}/matches/{match_id}").json()["data"]
        # Add the match to the set of interest if it's a shipwreck seed
        if match["seedType"] == "SHIPWRECK":
            all_runs.append(match)

    # Get name and time of the player and run
    player_times = []
    for run in all_runs:
        winner_uuid = run["result"]["uuid"]
        for player in run["players"]:
            if player["uuid"] == winner_uuid:
                winner_name = player["nickname"]
                break
        player_times.append((winner_name, run["result"]["time"]))

    # Sort by run time
    player_times.sort(key=lambda x: x[1])

    return player_times


def digital(raw_time):
    time = str(timedelta(milliseconds=raw_time))[3:7]
    return time


def get_altoid_stats():
    conn, cursor = db.start("mega_ranked.db")
    altoid_splits = {
        "story.enter_the_nether": [],
        "nether.find_bastion": [],
        "nether.find_fortress": [],
        "projectelo.timeline.blind_travel": [],
        "story.follow_ender_eye": [],
        "story.enter_the_end": [],
        "completion": [],
    }
    all_splits = {
        "story.enter_the_nether": [],
        "nether.find_bastion": [],
        "nether.find_fortress": [],
        "projectelo.timeline.blind_travel": [],
        "story.follow_ender_eye": [],
        "story.enter_the_end": [],
        "completion": [],
    }
    matches = db.query_db(
        cursor,
        table="matches",
        items="id, time, forfeited, result_uuid",
        type=2,
        season=7,
        decayed=False,
    ) + db.query_db(
        cursor,
        table="matches",
        items="id, time, forfeited, result_uuid",
        type=2,
        season=8,
        decayed=False,
    )
    full_lb = requests.get(f"{API_URL}/record-leaderboard").json()["data"]
    lb_ids = [match["id"] for match in full_lb]
    for match_id, time, forfeited, result_uuid in matches:
        runs = db.query_db(
            cursor,
            table="runs",
            items="timeline, player_uuid",
            match_id=match_id,
        )
        if match_id not in lb_ids and time < 429000 and not forfeited:
            print("Skipping cheated run", match_id, time)
            continue
        if match_id % 100 == 0:
            print(match_id)
        for timeline, uuid in runs:
            timeline = json.loads(timeline)
            splits = timeline_to_splits(timeline)
            splits["completion"] = time if forfeited == False and result_uuid == uuid else None
            for split in splits:
                if splits[split]:
                    all_splits[split].append(splits[split])
            if uuid == "d7d0b271136647fea7398a444ab51c13":
                for split in splits:
                    if splits[split]:
                        altoid_splits[split].append(splits[split])

    all_placements = {}
    all_length = {}
    all_performance = {}
    altoid_placements = {}
    altoid_length = {}
    altoid_performance = {}

    for split in all_splits:
        all_splits[split].sort()
        altoid_splits[split].sort()

        all_placements[split] = np.searchsorted(all_splits[split], PB_SPLITS[split])
        all_length[split] = len(all_splits[split])
        all_performance[split] = round(all_placements[split] / all_length[split] * 100, 3)
        altoid_placements[split] = np.searchsorted(altoid_splits[split], PB_SPLITS[split])
        altoid_length[split] = len(altoid_splits[split])
        altoid_performance[split] = round(altoid_placements[split] / altoid_length[split] * 100, 3)

    return all_placements, all_length, all_performance, altoid_placements, altoid_length, altoid_performance


def timeline_to_splits(timeline):
    return {
        "story.enter_the_nether": next((event["time"] for event in timeline if event["type"] == "story.enter_the_nether"), None),
        "nether.find_bastion": next((event["time"] for event in timeline if event["type"] == "nether.find_bastion"), None),
        "nether.find_fortress": next((event["time"] for event in timeline if event["type"] == "nether.find_fortress"), None),
        "projectelo.timeline.blind_travel": next((event["time"] for event in timeline if event["type"] == "projectelo.timeline.blind_travel"), None),
        "story.follow_ender_eye": next((event["time"] for event in timeline if event["type"] == "story.follow_ender_eye"), None),
        "story.enter_the_end": next((event["time"] for event in timeline if event["type"] == "story.enter_the_end"), None)
    }


def main_1():
    # Get stats in json form https://docs.mcsrranked.com/#users-identifier
    player_times = combine_lbs()
    for i, (player, time) in enumerate(player_times):
        print(f"#{i+1}: {digital(time)} // {player}")


def main_2():
    all_placements, all_length, all_performance, altoid_placements, altoid_length, altoid_performance = get_altoid_stats()
    print("Comparing to all runs since season 7")
    for split in all_placements:
        print(f"{split}: {all_placements[split]} / {all_length[split]} are faster than {digital(PB_SPLITS[split])} (Top {all_performance[split]}%)")

    print("Comparing to Altoid runs since season 7")
    for split in altoid_placements:
        print(f"{split}: {altoid_placements[split]} / {altoid_length[split]} are faster than {digital(PB_SPLITS[split])} (Top {altoid_performance[split]}%)")


if __name__ == "__main__":
    main_2()
