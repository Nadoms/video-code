import asyncio
import csv
from datetime import timedelta
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))
from rankedutils import db, api, constants, insight


def get_seed_insights(cursor):
    matches = db.query_db(cursor, where="seed_id IS NOT NULL", order="id").fetchall()
    seeds = db.query_db(cursor, table="seeds").fetchall()

    player_stats = {}
    seed_stats = {}

    for seed in seeds:
        (
            seed_id,
            overworld,
            bastion,
            structure_biome,
            bastion_biome,
            fortress_biome,
            structure_type,
            structure_contents,
            triples,
            singles,
            small_singles,
            good_gaps,
            o_level,
            tower,
            front_diagonal,
            front_straight,
            back_diagonal,
            back_straight,
            past_score,
            past_count,
            current_score,
            current_count,
            seasons,
            word_id
        ) = seed
        seed_stats[seed_id] = {
            "rolls": 0,
            "ranked_plays": 0,
            "acquire_iron": [],
            "end_enters": 0,
            "end_chokes": 0,
            "end_splits": [],
            "completions": 0,
            "record_holder": None,
            "record_time": None,
            "discovered_id": None,
            "discovered_date": None,
            "score": insight.get_seed_score(past_score, past_count, current_score, current_count, sample_size=1),
            "seasons": json.loads(seasons),
            "o_level": o_level,
            "overworld": overworld,
            "bastion": bastion,
            "triples": triples,
            "singles": singles,
            "small_singles": small_singles,
            "structure_biome": structure_biome,
            "bastion_biome": bastion_biome,
            "fortress_biome": fortress_biome,
        }

    for match in matches:
        (
            match_id,
            match_type,
            category,
            gameMode,
            result_uuid,
            time,
            forfeited,
            decayed,
            season,
            date,
            seedType,
            bastionType,
            tag,
            seed_id
        ) = match
        runs = db.query_db(cursor, table="runs", items="player_uuid, eloRate, timeline, score", match_id=match_id).fetchall()
        seed_stats[seed_id]["rolls"] += 1
        for uuid, elo, timeline, score in runs:
            timeline = list(reversed(json.loads(timeline)))
            if match_type != 2:
                raise FreakyError

            seed_stats[seed_id]["ranked_plays"] += 1
            if uuid not in player_stats:
                nick = db.get_nick(cursor, uuid)
                if not nick:
                    raise FreakyError
                player_stats[uuid] = {
                    "nickname": nick,
                    "seed_count": 0,
                    "seeds": [],
                    "repeats": 0,
                    "records": [],
                    "record_count": 0,
                }
            player_stats[uuid]["seed_count"] += 1
            if seed_id in player_stats[uuid]["seeds"]:
                player_stats[uuid]["repeats"] += 1
            else:
                player_stats[uuid]["seeds"].append(seed_id)

            iron_time = next((event["time"] for event in timeline if event["type"] == "story.smelt_iron"), None)
            if iron_time is not None:
                seed_stats[seed_id]["acquire_iron"].append(iron_time)

            death_events = ("projectelo.timeline.death", "projectelo.timeline.reset")
            end_enter = next((
                event["time"]
                for event
                in timeline
                if event["type"] == "story.enter_the_end"
            ), None)
            if end_enter is not None:
                end_choke = bool([
                    event["time"]
                    for event
                    in timeline
                    if event["type"] in death_events and event["time"] > end_enter
                ])
                seed_stats[seed_id]["end_enters"] += 1
                seed_stats[seed_id]["end_chokes"] += int(end_choke)
                if not forfeited and result_uuid == uuid:
                    seed_stats[seed_id]["end_splits"].append(time - end_enter)
                    seed_stats[seed_id]["completions"] += 1

                    if seed_stats[seed_id]["record_time"] is None or time < seed_stats[seed_id]["record_time"]:
                        seed_stats[seed_id]["record_time"] = time
                        seed_stats[seed_id]["record_holder"] = uuid

        if seed_stats[seed_id]["discovered_id"] is None:
            seed_stats[seed_id]["discovered_id"] = match_id
            seed_stats[seed_id]["discovered_date"] = date

    for seed_id in seed_stats:
        if seed_stats[seed_id]["record_holder"] is None:
            continue

        if seed_stats[seed_id]["record_holder"] not in player_stats:
            raise FreakyError

        player_stats[seed_stats[seed_id]["record_holder"]]["records"].append(seed_id)
        player_stats[seed_stats[seed_id]["record_holder"]]["record_count"] += 1

    return seed_stats, player_stats


class FreakyError(ValueError):

    def __init__(self, *args):
        super().__init__(*args)


def main():
    with db.connect() as c:
        seed_stats, player_stats = get_seed_insights(c)

    with open(ROOT_DIR / "data" / "seeds.json", mode="w") as f:
        json.dump(
            seed_stats,
            f,
            indent=4
        )
    with open(ROOT_DIR / "data" / "players.json", mode="w") as f:
        json.dump(
            player_stats,
            f,
            indent=4
        )

if __name__ == "__main__":
    main()
