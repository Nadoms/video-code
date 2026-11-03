import asyncio
import csv
from datetime import timedelta
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))
from rankedutils import db, api, constants, insight


def get_seed_insights():
    with db.connect() as c:
        matches = db.query_db(c)
        seeds = db.query_db(c, table="seeds").fetchall()

    seed_stats = {}
    default_stats = {
        "plays": 0,
        "end_enters": 0,
        "completions": 0,
        "discovered_id": None,
        "discovered_time": None,
        "score": None,
        "seasons": None,
        "o_level": None,
        "overworld": None,
        "bastion": None,
        "triples": None,
        "singles": None,
        "small_singles": None,
    }

    for seed in seeds:
        (
            id,
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
        seed_stats[seed] = {
        "plays": 0,
        "end_enters": 0,
        "completions": 0,
        "discovered_id": None,
        "discovered_time": None,
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
        


def main():
    with open(ROOT_DIR / "data" / f"seeds.json", mode="w") as f:
        json.dump(
            data,
            f,
            indent=4
        )

if __name__ == "__main__":
    data_type = "completions" if len(sys.argv) > 1 else "disparity"
    main(data_type)
