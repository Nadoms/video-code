import asyncio
import json
from pathlib import Path
from rankedutils import api, games

PLAYERS = ["doogile", "Lowk3y_"]
ROOT = Path(__file__).resolve().parent

async def get_player_data():
    player_data = {player: {} for player in PLAYERS}
    for player in PLAYERS:
        for season in range(1, 10):
            print(player, season)
            player_data[player][season] = {}
            player_response = api.User(player, season=season).get()
            _, detailed_matches = await games.get_detailed_matches(player_response, season, 0, 10000)
            player_data[player][season]["full"] = detailed_matches
            player_data[player][season]["comp"] = [
                match["result"]["time"]
                for match
                in detailed_matches
                if match["forfeited"] == False
                and match["result"]["uuid"] == player_response["uuid"]
            ]
            player_data[player][season]["end"] = [
                next(event["time"] for event in match["timelines"] if event["type"] == "story.enter_the_end")
                for match
                in detailed_matches
                if "story.enter_the_end" in (event["type"] for event in match["timelines"])
            ]
            player_data[player][season]["stronghold"] = [
                next(event["time"] for event in match["timelines"] if event["type"] == "story.follow_ender_eye")
                for match
                in detailed_matches
                if "story.follow_ender_eye" in (event["type"] for event in match["timelines"])
            ]
            player_data[player][season]["fortress"] = [
                next(event["time"] for event in match["timelines"] if event["type"] == "nether.find_fortress")
                for match
                in detailed_matches
                if "nether.find_fortress" in (event["type"] for event in match["timelines"])
            ]

    with open(ROOT / "data.json", "w") as f:
        json.dump(player_data, f, indent=4)


if __name__ == "__main__":
    asyncio.run(get_player_data())
