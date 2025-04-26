import json

import db


def find_completions():
    conn, cursor = db.start()
    matches = db.query_db(
        cursor,
        items="id, result_uuid, date, time, bastionType, seedType",
        type=2,
        decayed=False,
        forfeited=False,
    )
    completion_time = 0
    completions = 0
    data_points = []
    for match in matches:
        run = db.query_db(
            cursor,
            table="runs",
            items="eloRate",
            match_id=match[0],
            player_uuid=match[1],
        )[0]
        elo = run[0]
        completion_time += match[3]
        completions += 1
        data_points.append((match[2:4], elo, match[4:6]))

    avg_completion = completion_time / completions
    return avg_completion, data_points
