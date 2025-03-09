import json
import numpy as np
from pathlib import Path
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
    all_post_times = 0
    all_comp_times = 0
    all_comp_full = 0
    rank_times = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_comps = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_deaths = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_death_opps = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_entries = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_post_times = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_comp_times = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    rank_comp_full = {"coal": 0, "iron": 0, "gold": 0, "emerald": 0, "diamond": 0, "netherite": 0}
    netherite_times = []
    conn, cursor = db.start()
    matches = db.query_db(
        cursor,
        items="id, result_uuid, time, forfeited",
        bastionType=bastion.upper(),
        type=2,
        decayed=False,
    )
    for match in matches:
        runs = db.query_db(cursor, table="runs", items="eloRate, timeline, player_uuid", match_id=match[0])
        for run in runs:
            elo, timeline, uuid = run
            time = match[2] if match[1] == uuid and not match[3] else None
            total_time, deaths, completions, death_opps, entries, post_time, comp_time, full_comp, times = process_timeline(json.loads(timeline), time)
            if elo:
                rank = convert_to_rank(elo)
                rank_times[rank] += total_time
                rank_deaths[rank] += deaths
                rank_comps[rank] += completions
                rank_death_opps[rank] += death_opps
                rank_entries[rank] += entries
                rank_post_times[rank] += post_time
                rank_comp_times[rank] += comp_time
                rank_comp_full[rank] += full_comp
                if rank == "netherite":
                    netherite_times += times
            all_times += total_time
            all_comps += completions
            all_deaths += deaths
            all_death_opps += death_opps
            all_entries += entries
            all_post_times += post_time
            all_comp_times += comp_time
            all_comp_full += full_comp

    print(rank_times)
    print(rank_comps)
    print(rank_deaths)
    print(rank_death_opps)
    bastion_dict = {
        "mean": int(all_times / all_comps),
        "comps": all_comps,
        "deaths": all_deaths,
        "entries": all_entries,
        "death_rate": round(all_deaths / all_entries, 3),
        "post_mean": int(all_post_times / all_comp_full),
        "comp_mean": int(all_comp_times / all_comp_full),
        "rank_means": {rank: int(rank_times[rank] / rank_comps[rank]) for rank in RANKS},
        "rank_death_rates": {rank: round(rank_deaths[rank] / rank_death_opps[rank], 3) for rank in RANKS},
        "rank_post_means": {rank: int(rank_post_times[rank] / rank_comp_full[rank]) for rank in RANKS},
        "rank_comp_means": {rank: int(rank_comp_times[rank] / rank_comp_full[rank]) for rank in RANKS},
    }
    return bastion_dict, sorted(netherite_times)


def process_timeline(timeline, time, opponent_ended):
    deaths = 0
    death_opps = 0
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
    times = []
    for event in reversed(timeline):
        if event["type"] == "nether.find_bastion":
            bastion_entry = event["time"]
            entries += 1
            death_opps += 1

        elif event["type"] == "projectelo.timeline.reset":
            bastion_entry = 0
            bastion_exit = 0

        elif bastion_entry and not bastion_exit:
            if event["type"] == "projectelo.timeline.death":
                deaths += 1

            elif event["type"] in post_bastion:
                bastion_exit = event["time"]
                total_time += bastion_exit - bastion_entry
                times.append(bastion_exit - bastion_entry)
                completions += 1

    else:
        if opponent_ended and bastion_entry and not bastion_exit:
            death_opps -= 1

    if time and bastion_exit:
        post_time = time - bastion_exit
        full_comp = 1
    else:
        post_time = 0
        full_comp = 0
        time = 0

    return total_time, deaths, completions, death_opps, entries, post_time, time, full_comp, times


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
    bastion_splits_path = Path(__file__).parent / "data" / "bastion_splits.json"
    bastion_pace = {
        "bridge": {},
        "housing": {},
        "stables": {},
        "treasure": {},
    }
    bastion_splits = {
        "bridge": [],
        "housing": [],
        "stables": [],
        "treasure": [],
    }
    for bastion in BASTIONS:
        bastion_pace[bastion], bastion_splits[bastion] = process(bastion)
    bastion_pace_path.write_text(json.dumps(bastion_pace, indent=4))
    bastion_splits_path.write_text(json.dumps(bastion_splits, indent=4))


if __name__ == "__main__":
    main()
