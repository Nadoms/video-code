import asyncio
import csv
from datetime import timedelta
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
import db
import api


START_ID = 101000
INCREMENT = 1000
BATCH = 50
CURRENT_SEASON = 8
LAST_MATCHES = [0, 338896, 519261, 674675, 909751, 1168207, 1499236, 1970844, 2100000]
SPLIT_MAP = {
    "story.enter_the_nether": "ow",
    "nether.find_bastion": "nether",
    "nether.find_fortress": "bastion",
    "projectelo.timeline.blind_travel": "fortress",
    "story.follow_ender_eye": "blind",
    "story.enter_the_end": "stronghold",
}
eos = False


async def get_interest(id, season):
    cut_matches = {}
    print(f"Fetching matches before {id} for season {season}")
    matches = await api.RecentMatches(before=id, season=season, type=2, count=100).get_async()
    for match in matches:
        if match["forfeited"] is True:
            continue
        if match["id"] + 1000 > LAST_MATCHES[season] or id > LAST_MATCHES[season]:
            global eos
            eos = True
        winner_uuid = match["result"]["uuid"]
        winner_elo = next((change["eloRate"] for change in match["changes"] if change["uuid"] == winner_uuid))
        cut_matches[match["id"]] = {
            "date": match["date"],
            "time": match["result"]["time"],
            "elo": winner_elo,
            "ow": match["seed"]["overworld"],
            "bastion": match["seed"]["nether"],
        }
    return cut_matches


async def find_completions():
    current_id = START_ID
    season = 1
    all_matches = {}
    reached_end = False
    while not reached_end:
        ids = range(current_id, current_id + BATCH * INCREMENT, INCREMENT)
        try:
            match_groups = await asyncio.gather(
                *[get_interest(id, season) for id in ids]
            )
        except api.APINotFoundError:
            break

        for matches in match_groups:
            global eos
            if eos:
                season += 1
                current_id -= BATCH * INCREMENT
                eos = False
                if season > CURRENT_SEASON:
                    reached_end = True
            all_matches.update(matches)
        current_id += BATCH * INCREMENT

    total_time = timedelta(milliseconds=sum(
        match["time"] for match in all_matches.values()
    )).days

    return total_time, sorted(list(all_matches.values()), key=lambda x: x["date"])


async def find_disparity():
    all_matches = {}
    conn, cursor = db.start()
    matches = db.query_db(
        cursor,
        table="matches",
        items="id, seedType, bastionType",
        type=2,
        season=7,
        decayed=False
    )
    for id, ow_type, bastion_type in matches:
        disparity = {}
        run_1, run_2 = db.query_db(
            cursor,
            table="runs",
            items="eloRate, timeline",
            match_id=id
        )
        match_elo = int((run_1[0] + run_2[0]) / 2) if run_1[0] and run_2[0] else None
        timeline_1 = reversed(json.loads(run_1[1]))
        timeline_2 = reversed(json.loads(run_2[1]))
        previous_1 = 0
        previous_2 = 0
        for split in SPLIT_MAP:
            time_1 = next((event["time"] for event in timeline_1 if event["type"] == split), None)
            time_2 = next((event["time"] for event in timeline_2 if event["type"] == split), None)
            if not (time_1 and time_2):
                difference = None
                break
            split_1 = time_1 - previous_1
            split_2 = time_2 - previous_2
            difference = abs(split_1 - split_2)
            disparity[SPLIT_MAP[split]] = difference
            previous_1 = time_1
            previous_2 = time_2

        all_matches[id] = {
            "elo": match_elo,
            "o_type": ow_type,
            "b_type": bastion_type,
            **disparity
        }

    return list(all_matches.values())


def main(data_type):
    with open(ROOT_DIR / "playoffs_segment_2" / "data" / f"{data_type}.csv", mode="w", newline="") as csv_file:
        if data_type == "completions":
            total_time, all_matches = asyncio.run(find_completions())
            print(f"Total time: {total_time} days")
            writer = csv.DictWriter(csv_file, fieldnames=["date", "time", "elo", "bastion", "ow"])
        else:
            all_matches = asyncio.run(find_disparity())
            writer = csv.DictWriter(csv_file, fieldnames=["elo", "b_type", "o_type", "ow", "nether", "bastion", "fortress", "blind", "stronghold"])
        writer.writeheader()
        writer.writerows(all_matches)

if __name__ == "__main__":
    data_type = "completions" if len(sys.argv) > 1 else "disparity"
    main(data_type)
