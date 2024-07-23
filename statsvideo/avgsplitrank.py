import json
from os import path
import sys

def main(rank_no):
    full_times = [[], [], [], [], [], [], []]
    split_mapping = {
        "story.enter_the_nether": "ow",
        "nether.find_bastion": "nether",
        "nether.find_fortress": "bastion",
        "projectelo..blind_travel": "fortress",
        "story.follow_ender_eye": "blind",
        "story.enter_the_end": "stronghold",
        "rql.completed": "end"
    }
    event_mapping = {
        "story.enter_the_nether": "nether",
        "nether.find_bastion": "bastion",
        "nether.find_fortress": "fortress",
        "projectelo..blind_travel": "blind",
        "story.follow_ender_eye": "stronghold",
        "story.enter_the_end": "end",
        "rql.completed": "completed"
    }
    
    input = path.join("statsvideo", "data", f"splits_{rank_no}.txt")
    output = path.join("statsvideo", "data", f"splitrank.csv")
    with open(input, "r") as f:

        while True:
            timeline = f.readline().strip()
            if not timeline:
                break
            if timeline == "[]":
                continue

            good_timeline = tidy(timeline)
            
            prev_time = 0
            for i in range(len(good_timeline)):
                delta = good_timeline[i] - prev_time
                full_times[i].append(delta)
                prev_time = good_timeline[i]

    with open(output, "r") as f:
        lines = f.readlines()

    with open(output, "w") as f:
        f.write("ow,nether,bastion,fortress,blind,stronghold,end\n")
        for i in range(1, len(lines)):
            if rank_no + 1 != i:
                f.write(lines[i])
                continue
            line = ""
            for j in range(len(full_times)):
                avg = sum(full_times[j]) / len(full_times[j])
                line += str(round(avg))
                if j != len(full_times)-1:
                    line += ","
                else:
                    line += "\n"
                
            f.write(line)


def tidy(timeline):
    event_mapping = [
        "story.enter_the_nether",
        "nether.find_bastion",
        "nether.find_fortress",
        "projectelo.timeline.blind_travel",
        "story.follow_ender_eye",
        "story.enter_the_end",
        "rql.completed"
    ]

    good_timeline = []

    version = None

    if timeline[1:9] == "Timeline":
        timeline = timeline.split("),")
        version = True

    elif timeline[1] == "'":
        timeline = timeline.split("', ")
        version = False
    else:
        return good_timeline
    
    for i in range(len(timeline)):
        if version:
            event_arr = timeline[i][10:].split(", ")
            time = int(event_arr[0])
        else:
            event_arr = timeline[i].split()
            if event_arr[2][-1] == "]":
                event_arr[2] = event_arr[2][0:-2]
            time = get_raw_time(event_arr[2])
        
        if event_mapping[i] == event_arr[1]:
            good_timeline.append(time)
        else:
            return good_timeline

    return good_timeline


def get_raw_time(time):
    raw_time = 0
    time = list(reversed(time.split(":")))

    for i in range(len(time)):
        raw_time += int(time[i]) * (60 ** i)
    
    return raw_time * 1000


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        rank_no = int(sys.argv[1])
    else:
        print("Usage: python avgsplitrank.py <rank_no>")
    main(rank_no)