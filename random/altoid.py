from datetime import timedelta
import requests


API_URL = "https://mcsrranked.com/api"


def combine_lbs():
    # https://docs.mcsrranked.com/#record-leaderboard
    all_runs = []
    all_ids = set()
    full_lb = requests.get(f"{API_URL}/record-leaderboard").json()["data"]

    # Get the match IDs from the lifetime leaderboard
    for match in full_lb:
        # Don't bother with longer runs
        if match["time"] < 450000:
            all_ids.add(match["id"])
    # Get any extra matches from season leaderboards
    # Doing both bc lowk3y is missing off these and prob ranik too etc
    for season in range(1, 9):
        lb = requests.get(f"{API_URL}/record-leaderboard?season={season}").json()["data"]
        for match in lb:
            if match["time"] < 450000:
                all_ids.add(match["id"])

    print("Fetched leaderboards")

    # Get info about each match using https://docs.mcsrranked.com/#matches-matchid
    for match_id in all_ids:
        match = requests.get(f"{API_URL}/matches/{match_id}").json()["data"]
        # Add the match to the set of interest if it's a shipwreck seed
        if match["seedType"] == "SHIPWRECK":
            all_runs.append(match)

    # Get name and time of the player and run
    player_times = []
    for run in all_runs:
        winner_uuid = run["result"]["uuid"]
        for player in run["players"]:
            if player["uuid"] == winner_uuid:
                winner_name = player["nickname"]
                break
        player_times.append((winner_name, run["result"]["time"]))

    # Sort by run time
    player_times.sort(key=lambda x: x[1])

    return player_times


def digital(raw_time):
    time = str(timedelta(milliseconds=raw_time))[3:7]
    return time


def main():
    # Get stats in json form https://docs.mcsrranked.com/#users-identifier
    player_times = combine_lbs()
    for i, (player, time) in enumerate(player_times):
        print(f"#{i+1}: {digital(time)} // {player}")


if __name__ == "__main__":
    main()
