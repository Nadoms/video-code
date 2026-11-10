from collections import defaultdict
import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))
from rankedutils import db, insight, constants

BASTION_KEYS = ("triples", "singles", "small_singles")
SHIP_TYPES = ("full", "normal", "sideways", "upsidedown")
FORTRESS_BIOMES = ("basalt_deltas", "crimson_forest", "nether_wastes", "soul_sand_valley", "warped_forest")
ZERO_CYCLE = 60000
IRON_STEP = 2000
IRON_CAP = 120000
FORT_STEP = 5000
FORT_CAP = 600000
DISCOVERY_STEP = 1000
MIN_RECORD_RATE_SAMPLE = 50


def get_seed_stats(cursor):
    print("Collecting matches...")
    match_count = db.query_db(cursor, items="COUNT(*)", where="seed_id IS NOT NULL").fetchone()[0]
    matches = db.query_db(
        cursor.connection.cursor(),
        items="id, type, result_uuid, time, forfeited, date, seed_id",
        where="seed_id IS NOT NULL",
        order="id"
    )
    print("Collecting seeds...")
    seeds = db.query_db(cursor, table="seeds").fetchall()

    player_stats = {}
    seed_stats = {}

    print("Initialising seeds...")
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
            "iron_times": [],
            "fort_splits": [],
            "end_enters": 0,
            "end_chokes": 0,
            "end_splits": [],
            "completions": 0,
            "completion_time": 0,
            "record_holder": None,
            "record_time": None,
            "discovered_id": None,
            "discovered_date": None,
            "score": insight.get_seed_score(past_score, past_count, current_score, current_count, sample_size=1),
            "seasons": json.loads(seasons) if seasons is not None else None,
            "o_level": o_level,
            "overworld": overworld,
            "bastion": bastion,
            "triples": triples,
            "singles": singles,
            "small_singles": small_singles,
            "structure_biome": structure_biome,
            "bastion_biome": bastion_biome,
            "fortress_biome": fortress_biome,
            "structure_type": structure_type,
            "structure_contents": json.loads(structure_contents) if structure_contents is not None else None
        }

    for i, match in enumerate(matches):
        if i % 10000 == 0:
            print(f"Gathering match data... ({i // 10000}/{match_count // 10000})", end="\r")
        (
            match_id,
            match_type,
            result_uuid,
            time,
            forfeited,
            date,
            seed_id
        ) = match
        runs = db.query_db(cursor, table="runs", items="player_uuid, eloRate, timeline, score", match_id=match_id).fetchall()
        seed_stats[seed_id]["rolls"] += 1
        for uuid, _, timeline, score in runs:
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
                    "seeds": set(),
                    "play_count": 0,
                    "repeats": [],
                    "repeat_count": 0,
                    "records": [],
                    "record_count": 0,
                }
            player_stats[uuid]["play_count"] += 1
            if seed_id in player_stats[uuid]["seeds"]:
                player_stats[uuid]["repeats"].append(seed_id)
                player_stats[uuid]["repeat_count"] += 1
            else:
                player_stats[uuid]["seeds"].add(seed_id)

            iron_time = next((event["time"] for event in timeline if event["type"] == "story.smelt_iron"), None)
            if iron_time is not None:
                seed_stats[seed_id]["iron_times"].append(iron_time)

            fort_enter = next((
                event["time"]
                for event
                in timeline
                if event["type"] == "nether.find_fortress"
            ), None)
            sh_enter = next((
                event["time"]
                for event
                in timeline
                if event["type"] == "story.follow_ender_eye"
            ), None)
            if fort_enter is not None and sh_enter is not None and sh_enter > fort_enter:
                seed_stats[seed_id]["fort_splits"].append(sh_enter - fort_enter)

            death_events = ("projectelo.timeline.death", "projectelo.timeline.reset")
            end_enter = next((
                event["time"]
                for event
                in timeline
                if event["type"] == "story.enter_the_end"
            ), None)
            if end_enter is None:
                continue
            end_choke = any(
                event["type"] in death_events and event["time"] > end_enter
                for event
                in timeline
            )
            seed_stats[seed_id]["end_enters"] += 1
            seed_stats[seed_id]["end_chokes"] += int(end_choke)
            if not forfeited and result_uuid == uuid:
                seed_stats[seed_id]["end_splits"].append(time - end_enter)
                seed_stats[seed_id]["completions"] += 1
                seed_stats[seed_id]["completion_time"] += time

                if seed_stats[seed_id]["record_time"] is None or time < seed_stats[seed_id]["record_time"]:
                    seed_stats[seed_id]["record_time"] = time
                    seed_stats[seed_id]["record_holder"] = uuid

        if seed_stats[seed_id]["discovered_id"] is None:
            seed_stats[seed_id]["discovered_id"] = match_id
            seed_stats[seed_id]["discovered_date"] = date

    print("Awarding records...")
    for seed_id, seed_stat in seed_stats.items():
        if seed_stat["record_holder"] is None:
            continue

        if seed_stat["record_holder"] not in player_stats:
            raise FreakyError

        player_stats[seed_stat["record_holder"]]["records"].append(seed_id)
        player_stats[seed_stat["record_holder"]]["record_count"] += 1

    print("Tidying up...")
    for player_stat in player_stats.values():
        player_stat["unique_seeds"] = len(player_stat["seeds"])
        player_stat["record_rate"] = ratio(player_stat["record_count"], player_stat["play_count"])
        player_stat.pop("seeds")
        player_stat.pop("records")

    return seed_stats, player_stats


class FreakyError(ValueError):

    def __init__(self, *args):
        super().__init__(*args)


def analyse_seeds(seed_stats, player_stats):
    """
    Information to gather:
    - Most played seed of all time
    - Most completed seed of all time
    - Best seed of all time (with seed score)
    - Worst seed of all time (with seed score)
    - Number of seeds
    - Which player has the record on the most seeds and how many
    - Which player has the highest record-rate (records / unique seeds played) with higher than 50 sample size
    - Proportion of players who have had a repeat seed
    - Number of players
    - The first match 
    - Info for graph of player repeat seed encounters / player play_count
    - Info for distribution of seed playcounts
    - Info for distribution of o-levels
    - Info for distribution of triples / singles / small singles for housing / stables / bridge bastion variants
    - Info for graph of zero-cycle rate per o-level, where zero-rate is (number of endfights < 60s) / (number of end enters)
    - Info for graph of end choke rate per o-level, where end choke rate is (number of end chokes) / (number of end enters)
    - Info for distribution of biomes for village overworlds
    - Info for distribution of acquiring iron for each seed type, and all seed types
    - Info for graph of avg acquire iron time for each shipwreck overworld type (and their distributions ig)
    - Info for graph of avg acquire iron time for each shipwreck variation (structure_type) and their distributions
    - Info for graph of number of seeds discovered / match ID (resolution of per 1000 match IDs)
    - Info for distribution of all seed scores with their sample sizes (in ordered list of tuples)
    - Info for graph of avg completion time per item in structure contents
    """
    most_played = {"seed_id": None, "plays": 0}
    most_completed = {"seed_id": None, "completions": 0}
    first_match = {"match_id": None, "date": None}
    scored_seeds = []
    playcounts = defaultdict(int)
    o_levels = defaultdict(int)
    o_level_ends = defaultdict(lambda: {"end_enters": 0, "end_chokes": 0, "completions": 0, "zero_cycles": 0})
    bastion_biomes = defaultdict(int)
    fortress_biomes = defaultdict(int)
    village_biomes = defaultdict(int)
    iron_all = defaultdict(int)
    discoveries = defaultdict(int)
    bastion_counts = defaultdict(lambda: {key: defaultdict(int) for key in BASTION_KEYS})
    iron_overworld = {
        overworld: defaultdict(int)
        for overworld in constants.OVERWORLDS
    }
    iron_shipwreck = {
        ship_type: defaultdict(int)
        for ship_type in SHIP_TYPES
    }
    item_times = {
        overworld: defaultdict(lambda: {"count": 0, "total": 0, "non_count": 0, "non_total": 0})
        for overworld in constants.OVERWORLDS
    }
    fortress_splits = {
        biome: defaultdict(int)
        for biome in FORTRESS_BIOMES
    }

    print("Extracting seed data...")
    for seed_id, seed in seed_stats.items():
        if seed["rolls"] == 0:
            continue

        if seed["rolls"] > most_played["plays"]:
            most_played = {"seed_id": seed_id, "plays": seed["rolls"]}
        if seed["completions"] > most_completed["completions"]:
            most_completed = {"seed_id": seed_id, "completions": seed["completions"]}
        if first_match["match_id"] is None or seed["discovered_id"] < first_match["match_id"]:
            first_match = {"match_id": seed["discovered_id"], "date": seed["discovered_date"]}

        if seed["score"] is not None:
            scored_seeds.append((seed["score"], seed["completions"], seed_id))
        playcounts[seed["rolls"]] += 1
        o_levels[seed["o_level"]] += 1
        discoveries[seed["discovered_id"] // DISCOVERY_STEP * DISCOVERY_STEP] += 1

        for key in BASTION_KEYS:
            bastion_counts[seed["bastion"]][key][seed[key]] += 1

        ends = o_level_ends[seed["o_level"]]
        ends["end_enters"] += seed["end_enters"]
        ends["end_chokes"] += seed["end_chokes"]
        ends["completions"] += seed["completions"]
        ends["zero_cycles"] += sum(split < ZERO_CYCLE for split in seed["end_splits"])

        bastion_biomes[seed["bastion_biome"]] += 1
        fortress_biomes[seed["fortress_biome"]] += 1
        if seed["overworld"] == "VILLAGE":
            village_biomes[seed["structure_biome"]] += 1

        for iron_time in seed["iron_times"]:
            iron_band = min(iron_time, IRON_CAP) // IRON_STEP * IRON_STEP
            iron_all[iron_band] += 1
            iron_all["avg"] += iron_time
            iron_overworld[seed["overworld"]][iron_band] += 1
            iron_overworld[seed["overworld"]]["avg"] += iron_time
            if seed["overworld"] == "SHIPWRECK" and seed["structure_type"]:
                iron_shipwreck[seed["structure_type"]][iron_band] += 1
                iron_shipwreck[seed["structure_type"]]["avg"] += iron_time

        for fort_split in seed["fort_splits"]:
            fort_band = min(fort_split, FORT_CAP) // FORT_STEP * FORT_STEP
            fortress_splits[seed["fortress_biome"]][fort_band] += 1
            fortress_splits[seed["fortress_biome"]]["avg"] += fort_split

        if seed["structure_contents"] is not None and seed["completions"] > 0:
            avg_completion = seed["completion_time"] / seed["completions"]
            for item in ("golden_carrot", "egap", "carrot", "diamond", "looting_sword", "obsidian"):
                present = "non_" if item not in seed["structure_contents"] else ""
                item_times[seed_stats[seed_id]["overworld"]][item][f"{present}count"] += 1
                item_times[seed_stats[seed_id]["overworld"]][item][f"{present}total"] += avg_completion

    scored_seeds.sort()
    filtered_scored_seeds = [s for s in scored_seeds if s[1] > 5]
    best_score, best_plays, best_seed = filtered_scored_seeds[-1]
    worst_score, worst_plays, worst_seed = filtered_scored_seeds[0]

    repeat_players = 0
    most_records = {"nickname": None, "records": 0}
    best_record_rate = {"nickname": None, "record_rate": 0}
    repeat_points = []

    print("Extracting record data...")
    for player in player_stats.values():
        repeat_players += player["repeat_count"] > 0
        repeat_points.append((player["play_count"], player["repeat_count"]))

        if player["record_count"] > most_records["records"]:
            most_records = {"nickname": player["nickname"], "records": player["record_count"]}

        if player["unique_seeds"] > MIN_RECORD_RATE_SAMPLE:
            record_rate = player["record_rate"]
            if record_rate > best_record_rate["record_rate"]:
                best_record_rate = {"nickname": player["nickname"], "record_rate": record_rate}

    print("Constructing final insights...")
    stats = {
        "most_played_seed": most_played,
        "most_completed_seed": most_completed,
        "best_seed": {"seed_id": best_seed, "score": best_score, "sample_size": best_plays},
        "worst_seed": {"seed_id": worst_seed, "score": worst_score, "sample_size": worst_plays},
        "seed_count": len(scored_seeds),
        "most_records": most_records,
        "best_record_rate": best_record_rate,
        "repeat_player_rate": ratio(repeat_players, len(player_stats)),
        "player_count": len(player_stats),
        "first_match": first_match,
    }
    distributions = {
        "seed_playcount_distribution": sorted_stats(playcounts),
        "o_level_distribution": sorted_stats(o_levels),
        "bastion_distribution": {
            bastion: {key: sorted_stats(counts[key]) for key in BASTION_KEYS}
            for bastion, counts in bastion_counts.items()
        },
        "bastion_biomes": sorted_stats(bastion_biomes),
        "fortress_biomes": sorted_stats(fortress_biomes),
        "village_biomes": sorted_stats(village_biomes),
        "iron_distribution": sorted_stats(iron_all),
        "iron_overworld": {
            overworld: sorted_stats(distribution)
            for overworld, distribution in iron_overworld.items()
        },
        "iron_shipwreck": {
            structure_type: sorted_stats(distribution)
            for structure_type, distribution in iron_shipwreck.items()
        },
        "fortress_biome_splits": {
            biome: sorted_stats(distribution)
            for biome, distribution in fortress_splits.items()
        },
    }
    graphs = {
        "avg_per_item": {
            overworld: {
                item: {
                    "present": ratio(times["total"], times["count"], dp=0),
                    "absent": ratio(times["non_total"], times["non_count"], dp=0),
                }
                for item, times in item_times[overworld].items()
            } for overworld in item_times
        },
        "o_level_stats": {
            o_level: {
                "zero_cycle_rate": ratio(ends["zero_cycles"], ends["completions"]),
                "end_choke_rate": ratio(ends["end_chokes"], ends["end_enters"]),
            }
            for o_level, ends in sorted_stats(o_level_ends).items()
        },
        "discovery_history": sorted_stats(discoveries),
        "repeats_play_count": sorted(repeat_points),
        "seed_scores": [(score, plays) for score, plays, _ in scored_seeds],
    }
    return stats, distributions, graphs


def ratio(numerator, denominator, dp=3):
    if not denominator:
        return None
    if dp == 0:
        return int(numerator / denominator)
    return round(numerator / denominator, dp)


def sorted_stats(stat):
    if "avg" in stat:
        total = sum(stat[key] for key in stat if key != "avg")
        stat["avg"] = ratio(stat["avg"], total, dp=0)
    return dict(sorted(stat.items(), key=lambda item: (item[0] == "avg", item[0] is None, item[0])))


def main(reload=True):
    if reload:
        with db.connect() as c:
            seed_stats, player_stats = get_seed_stats(c)
        with open(ROOT_DIR / "data" / "seeds.json", mode="w") as f:
            json.dump(seed_stats, f, indent=4)
        with open(ROOT_DIR / "data" / "players.json", mode="w") as f:
            json.dump(player_stats, f, indent=4)
    else:
        with open(ROOT_DIR / "data" / "seeds.json", mode="r") as f:
            seed_stats = json.load(f)
        with open(ROOT_DIR / "data" / "players.json", mode="r") as f:
            player_stats = json.load(f)

    stats, distributions, graphs = analyse_seeds(seed_stats, player_stats)
    with open(ROOT_DIR / "data" / "stats.json", mode="w") as f:
        json.dump(stats, f, indent=4)
    with open(ROOT_DIR / "data" / "distributions.json", mode="w") as f:
        json.dump(distributions, f, indent=4)
    with open(ROOT_DIR / "data" / "graphs.json", mode="w") as f:
        json.dump(graphs, f, indent=4)

if __name__ == "__main__":
    main(reload=True)
