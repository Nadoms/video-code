import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import db

SPLIT_MAP = {
    "story.enter_the_nether": "ow",
    "nether.find_bastion": "nether",
    "nether.find_fortress": "bastion",
    "projectelo.timeline.blind_travel": "fortress",
    "story.follow_ender_eye": "blind",
    "story.enter_the_end": "stronghold",
}
SPLITS = ["ow", "nether", "bastion", "fortress", "blind", "stronghold", "end"]
RANKS = [600, 900, 1200, 1500, 2000, 3000]


def analyse_ratios():
    conn, cursor = db.start()
    matches = db.query_db(
        cursor,
        items="id, result_uuid, time",
        type=2,
        forfeited=False,
        decayed=False,
        season=7,
    )
    print(f"Analysing {len(matches)} matches")
    completion_time = 0
    completions = 0
    ranked_completion_time = {rank: 0 for rank in RANKS}
    ranked_completions = {rank: 0 for rank in RANKS}
    split_times = {split: 0 for split in SPLITS}
    splits = {split: 0 for split in SPLITS}
    ranked_split_times = {rank: {split: 0 for split in SPLITS} for rank in RANKS}
    ranked_splits = {rank: {split: 0 for split in SPLITS} for rank in RANKS}
    for match in matches:
        runs = db.query_db(
            cursor,
            table="runs",
            items="eloRate, timeline, player_uuid",
            match_id=match[0]
        )
        for run in runs:
            elo, timeline, uuid = run
            if match[1] != uuid:
                continue
            completion_time += match[2]
            completions += 1
            timeline = list(reversed(json.loads(timeline)))
            previous = 0
            for split_name in SPLIT_MAP:
                time = next((event["time"] for event in timeline if event["type"] == split_name), None)
                if time is None:
                    print(f"Missing split {split_name} for match {match[0]}")
                    break
                split_time = time - previous
                previous = time
                if split_time < 0:
                    break

                split_short = SPLIT_MAP[split_name]
                split_times[split_short] += split_time
                splits[split_short] += 1
                if elo:
                    for max_elo in RANKS:
                        if elo < max_elo:
                            ranked_split_times[max_elo][split_short] += split_time
                            ranked_splits[max_elo][split_short] += 1
                            break
            end_time = match[2] - previous
            split_times["end"] += end_time
            splits["end"] += 1
            if elo:
                for max_elo in RANKS:
                    if elo < max_elo:
                        ranked_completion_time[max_elo] += match[2]
                        ranked_completions[max_elo] += 1
                        ranked_split_times[max_elo]["end"] += end_time
                        ranked_splits[max_elo]["end"] += 1
                        break

    average_split_times = {split: round(split_times[split] / splits[split]) for split in SPLITS}
    ranked_average_split_times = {rank: {split: round(ranked_split_times[rank][split] / ranked_splits[rank][split]) for split in SPLITS} for rank in RANKS}

    print(f"Total completion time: {completion_time}")
    print(f"Total completions: {completions}")
    print(f"Average completion time: {completion_time / completions}")
    print(f"Ranked total completion time: {ranked_completion_time}")
    print(f"Ranked total completions: {ranked_completions}")
    print("Ranked average completion time:", {rank: (ranked_completion_time[rank] / ranked_completions[rank]) for rank in RANKS})
    print(f"Total split times: {split_times}")
    print(f"Total splits: {splits}")
    print("Average split times:", average_split_times)
    print(f"Ranked total split times: {ranked_split_times}")
    print(f"Ranked total splits: {ranked_splits}")
    print("Ranked average split times:", ranked_average_split_times)

    split_ratio = {split: round(split_times[split] / completion_time, 3) for split in SPLITS}
    ranked_split_ratio = {rank: {split: round(ranked_split_times[rank][split] / ranked_completion_time[rank], 3) for split in SPLITS} for rank in RANKS}
    print("Split proportions:", split_ratio)
    print("Ranked split proportions:", ranked_split_ratio)

    return split_ratio, splits, average_split_times, ranked_split_ratio, ranked_splits, ranked_average_split_times


def main():
    split_ratio, splits, average_split_times, ranked_split_ratio, ranked_splits, ranked_average_split_times = analyse_ratios()
    with open(ROOT_DIR / "random" / "split_ratio.json", "w") as f:
        json.dump(
            {
                "split_ratio": split_ratio,
                "split_samples": splits,
                "split_avg": average_split_times,
                "ranked_split_ratio": ranked_split_ratio,
                "ranked_split_samples": ranked_splits,
                "ranked_split_avg": ranked_average_split_times,
            },
            f,
            indent=4
        )


if __name__ == "__main__":
    main()
