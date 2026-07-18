import json
from collections import Counter
from rankedutils import db, constants, api
from pathlib import Path


DATA_DIR = Path(__file__).parent / "data"


def collect_advancements(season):
    _, cursor = db.start("/home/nadoms/pers_repos/video-code/ranked.db")
    matches = db.query_db(
        cursor,
        items="id, forfeited, time, result_uuid",
        season=season,
        type=2,
    )
    advancements = Counter()
    noted_matches = {}
    wither_lb = {}
    for match_id, forfeited, time, result_uuid in matches:
        if not forfeited and time < 340000:
            print(f"Cheated run: {match_id}")
            continue
        if match_id % 1000 == 0:
            print(match_id)
        timelines = db.query_db(
            cursor,
            table="runs",
            items="timeline, player_uuid",
            match_id=match_id
        )
        for timeline in timelines:
            timeline, player_uuid = timeline
            for event in json.loads(timeline):
                if event["type"] in INTERESTING_ADV:
                    try:
                        a = api.Match(match_id).get(force_request=True)
                    except api.APINotFoundError:
                        print(f"Cheated run (sneaky): {match_id}")
                        break
                    if match_id in [2932122, 2016184, 4101168, 4101532, 4101620, 4101756, 4135884, 4136378, 4136417]:
                        print(f"Cheated run (sneakyy): {match_id}")
                        break
                    noted_matches[match_id] = event["type"]
                advancements[event["type"]] += 1

                if event["type"] == "nether.summon_wither":
                    wither_lb[match_id] = {
                        "completion": time if not forfeited and result_uuid == player_uuid else None,
                        "wither": event["time"],
                        "uuid": player_uuid,
                    }

    return advancements, noted_matches, len(matches), wither_lb


def main():
    all_advancements = Counter()
    all_noted_matches = {}
    all_count = 0
    all_wither_lb = {}
    for season in range(1, 11):
        advancements, noted_matches, count, wither_lb = collect_advancements(season)
        all_advancements += advancements
        all_noted_matches.update(noted_matches)
        all_count += count
        all_wither_lb.update(wither_lb)
    with open(DATA_DIR / "advancements_post_fixed.txt", "w") as f:
        f.write(f"{all_count * 2:>7}: total runs\n")
        for i, (advancement, count) in enumerate(all_advancements.most_common()):
            f.write(f"#{len(all_advancements)-i}: {advancement} ({(count / all_count * 50):.2f}%; {count})\n")

    print(all_wither_lb)
    print(json.dumps(all_noted_matches, indent=4))


if __name__ == "__main__":
    main()
