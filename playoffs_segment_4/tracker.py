import json
import math
import csv
from collections import Counter
from rankedutils import db, constants, api
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"
START_DATE = 1734739200
END_DATE = 1767312000


def collect_info(season):
    match_info = {}
    _, cursor = db.start("/home/nadoms/pers_repos/video-code/ranked.db")
    matches = db.query_db(
        cursor,
        items="id, forfeited, time, date, type",
        season=season,
    )
    for match_id, forfeited, time, date, match_type in matches:
        if not forfeited and time < 340000 and match_type == 2:
            print(f"Cheated run: {match_id}")
            continue
        if match_id % 1000 == 0:
            print(match_id)
        if match_type == 2:
            elos = db.query_db(
                cursor,
                table="runs",
                items="eloRate",
                match_id=match_id
            )
        else:
            elos = None
        match_info[match_id] = {
            "date_start": date,
            "date_end": date + int(time / 1000),
            "type": match_type,
            "elo": elos
        }

    return match_info


def extract_playercount(all_match_info, bucket=1800):
    events = []
    
    # Track total matches that have started
    match_start_times = {}
    
    for match_id, match in all_match_info.items():
        match_start_times[match_id] = match["date_start"]
        events.append((match["date_start"], 0, match_id))
        events.append((match["date_end"], 2, match_id))
    
    bucket_times = list(range(START_DATE, END_DATE + 1, bucket))
    for bucket_time in bucket_times:
        events.append((bucket_time, 1, bucket_time))
    
    events.sort(key=lambda x: (x[0], x[1]))
    
    # Sweep through events
    results = []
    active_matches = set()
    matches_started_ids = set()
    bucket_idx = 0
    
    for timestamp, event_type, data in events:
        if event_type == 0:  # Match start
            active_matches.add(data)
            matches_started_ids.add(data)
        elif event_type == 2:  # Match end
            active_matches.discard(data)
        elif event_type == 1:  # Bucket query
            concurrent_count = len(active_matches)
            total_matches = len(matches_started_ids)
            results.append({
                'date': data,
                'concurrent_matches': concurrent_count,
                'total_matches': total_matches
            })
            bucket_idx += 1
            if bucket_idx % 100 == 0:
                print(f"Processed {bucket_idx}/{len(bucket_times)} buckets - Date {data}: {concurrent_count} concurrent, {total_matches} total")
    
    return results


def main():
    # all_match_info = {}
    # for season in range(7, 10):
    #     all_match_info.update(collect_info(season))
    # with open(DATA_DIR / "match_info.json", "w") as f:
    #     json.dump(all_match_info, f, indent=4)

    with open(DATA_DIR / "match_info.json", "r") as f:
        all_match_info = json.load(f)

    results = extract_playercount(all_match_info)
    
    # Write to CSV
    with open(DATA_DIR / "tracker.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'concurrent_matches', 'total_matches'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\nWrote {len(results)} rows to tracker.csv")


if __name__ == "__main__":
    main()
