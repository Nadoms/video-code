import asyncio
import csv
import json
from pathlib import Path
import sys


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
import api


START_ID = 101000
INCREMENT = 1000
BATCH = 50
CURRENT_SEASON = 8
LAST_MATCHES = [0, 338896, 519261, 674675, 909751, 1168207, 1499236, 1970844, 2100000]
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
        winner_elo = next((player["eloRate"] for player in match["players"] if player["uuid"] == winner_uuid))

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
                eos = False
                if season > CURRENT_SEASON:
                    reached_end = True
            all_matches.update(matches)
        current_id += BATCH * INCREMENT

    return sorted(list(all_matches.values()), key=lambda x: x["date"])


def main():
    all_matches = asyncio.run(find_completions())
    with open(ROOT_DIR / "playoffs_segment_2" / "data" / "completions.csv", mode="w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["date", "time", "elo", "bastion", "ow"])
        writer.writeheader()
        writer.writerows(all_matches)

if __name__ == "__main__":
    main()
