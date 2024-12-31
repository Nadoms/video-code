import json
import numpy as np
from pathlib import Path
import re

BASTIONS = ["bridge", "housing", "stables", "treasure"]
RANKS = ["coal", "iron", "gold", "emerald", "diamond", "netherite"]
TIME_PATTERN = r"^.*\s(\d:\d\d:\d\d)"


def process(bastion):
    times = []
    ranks = {
        "coal": 0,
        "iron": 0,
        "gold": 0,
        "emerald": 0,
        "diamond": 0,
        "netherite": 0,
    }
    for i in range(len(RANKS)):
        rank_times = []
        with open(Path(__file__).parent / "data" / bastion / f"{i}.txt") as b:
            while True:
                line = b.readline()
                if not line:
                    break
                match = re.search(TIME_PATTERN, line)
                if match:
                    time = get_raw_time(match.group(1))
                    rank_times.append(time)
        times.extend(rank_times)
        ranks[RANKS[i]] = int(np.array(rank_times).mean())

    mean = int(np.array(times).mean())
    median = int(np.median(times))
    count = len(times)
    return mean, median, count, ranks


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
        bastion_pace[bastion]["mean"], bastion_pace[bastion]["median"], bastion_pace[bastion]["count"], bastion_pace[bastion]["ranks"] = process(bastion)
    bastion_pace_path.write_text(json.dumps(bastion_pace, indent=4))


if __name__ == "__main__":
    main()
