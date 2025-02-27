import json
import numpy as np
from pathlib import Path
import re
import sqlite3
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import db

BASTIONS = ["bridge", "housing", "stables", "treasure"]
RANKS = ["coal", "iron", "gold", "emerald", "diamond", "netherite"]
TIME_PATTERN = r"^.*\s(\d:\d\d:\d\d)"


def process(bastion):
    all_times = 0
    all_comps = 0
    all_deaths = 0
    all_entries = 0
    rank_times = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_comps = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_deaths = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_entries = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    conn, cursor = db.start()
    ids = db.query_db(
        cursor,
        items="id",
        bastionType=bastion.upper(),
        type=2,
        decayed=False,
    )
    for id in ids:
        runs = db.query_db(cursor, table="runs", items="eloRate, timeline", match_id=id[0])
        for run in runs:
            elo, timeline = run
            total_time, deaths, completions, entries = process_timeline(json.loads(timeline))
            if elo:
                rank = convert_to_rank(elo)
                rank_times[rank] += total_time
                rank_deaths[rank] += deaths
                rank_comps[rank] += completions
                rank_entries[rank] += entries
            all_times += total_time
            all_comps += completions
            all_deaths += deaths
            all_entries += entries

    print(rank_times)
    print(rank_comps)
    print(rank_deaths)
    print(rank_entries)
    bastion_dict = {
        "mean": int(all_times / all_comps),
        "comps": all_comps,
        "deaths": all_deaths,
        "entries": all_entries,
        "death_rate": round(all_deaths / all_entries, 3),
        "rank_means": {rank: int(rank_times[rank] / rank_comps[rank]) for rank in RANKS},
        "rank_death_rates": {rank: round(rank_deaths[rank] / rank_entries[rank], 3) for rank in RANKS},
    }
    return bastion_dict


def process_timeline(timeline):
    deaths = 0
    total_time = 0
    entries = 0
    completions = 0
    post_bastion = [
        "nether.find_fortress",
        "projectelo.timeline.blind_travel",
        "story.follow_ender_eye",
        "story.enter_the_end",
    ]
    bastion_entry = 0
    bastion_exit = 0
    for event in reversed(timeline):
        if event["type"] == "nether.find_bastion":
            bastion_entry = event["time"]
            entries += 1

        elif event["type"] == "projectelo.timeline.reset":
            bastion_entry = 0
            bastion_exit = 0

        elif bastion_entry and not bastion_exit:
            if event["type"] == "projectelo.timeline.death":
                deaths += 1

            elif event["type"] in post_bastion:
                bastion_exit = event["time"]
                total_time += bastion_exit - bastion_entry
                completions += 1

    return total_time, deaths, completions, entries


def convert_to_rank(elo):
    if not elo:
        return "unranked"
    if elo < 600:
        return "coal"
    if elo < 900:
        return "iron"
    if elo < 1200:
        return "gold"
    if elo < 1500:
        return "emerald"
    if elo < 2000:
        return "diamond"
    if elo >= 2000:
        return "netherite"
    return "unranked"


def get_raw_time(time):
    raw_time = 0
    time = list(reversed(time.split(":")))

    for i, value in enumerate(time):
        raw_time += int(value) * (60 ** i)

    return raw_time * 1000


def main():
    bastion_pace_path = Path(__file__).parent / "data" / "bastion_pace.json"
    bastion_pace = {
        "bridge": {},
        "housing": {},
        "stables": {},
        "treasure": {},
    }
    for bastion in BASTIONS:
        bastion_pace[bastion] = process(bastion)
    bastion_pace_path.write_text(json.dumps(bastion_pace, indent=4))


if __name__ == "__main__":
    main()
