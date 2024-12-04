from datetime import datetime
from dijkstar import Graph
import json
import os
import unicodedata
from rapidfuzz import process
import bisect


base_path = os.path.join(os.getcwd(), "Core", "static")

# marge files to one file
stations_times = {f"line_{i}": json.load(open(f"stations_{i}.json", "r", encoding="UTF-8")) for i in range(1, 8)}

# marge these lines to one
stations = json.load(open(f"stations.json", "r", encoding="utf-8"))
lines = {f"line_{m}": stations["stations"][f"line_{m}"] for m in range(1, 8)}


stations_names = []
for line in lines.values():
    stations_names.extend(line)

terminals = {line_name: [line[0], line[-1]] for line_name, line in lines.items()}

line_lookup = {}
for line, stations in lines.items():
    for i in range(len(stations) - 1):
        line_lookup[(stations[i], stations[i + 1])] = line
        line_lookup[(stations[i + 1], stations[i])] = line

# delete this function
def normalize_str(s) -> str: 

    return unicodedata.normalize("NFC", s).strip()


def find_closest_word(input_word, word_list, score_threshold=70) -> str:
    closest_match, score, _ = process.extractOne(input_word, word_list)
    return closest_match if score > score_threshold else None


def find_terminal_direction(line, current_station, next_station) -> str:

    return terminals[line][1] if lines[line].index(current_station) < lines[line].index(next_station) else terminals[line][0]



# optimize this fucking function
def is_time_valid(time_str):
    return time_str not in [None, "", "None", "none"]


def get_next_time(station_times, current_time):
    current_time = datetime.strptime(current_time, "%H:%M") if not isinstance(current_time, datetime) else current_time
    
    no_schedule_flag = False

    for time_str in station_times:
        if not is_time_valid(time_str):
            no_schedule_flag = True
            continue

        next_time = datetime.strptime(time_str, "%H:%M")
        if next_time > current_time:
            formatted_time = next_time.strftime("%H:%M")
            return formatted_time, no_schedule_flag
    return None, no_schedule_flag


def add_overview_entry(overview, station_name, time, line_name, is_line_change, message="") -> None:

    overview.append({
        "station_name": station_name,
        "time": time,
        "color": get_line_color(line_name),
        "is_line_change": is_line_change,
        "message": message
    })

def add_travel_guide_entry(flag, travel_guide, station_name, line_name, terminal) -> None:
    if flag == "source".lower():
        travel_guide.append(f"در ایستگاه {station_name} وارد خط {line_name} شوید و به سمت {terminal} سوار مترو شوید.")
    elif flag == "change".lower():
        travel_guide.append(f"در ایستگاه {station_name} از مترو پیاده شوید. سپس وارد خط {line_name} شده و به سمت {terminal} سوار مترو شوید.")
    elif flag == "destination".lower():
        travel_guide.append(f"در ایستگاه {station_name} از مترو پیاده شوید و از ایستگاه خارج شوید. ")

def get_line_color(line_name) -> str:

    line_colors = {
        "line_1": "قرمز",
        "line_2": "آبی",
        "line_3": "آبی آسمانی",
        "line_4": "زرد",
        "line_5": "سبز",
        "line_6": "صورتی",
        "line_7": "بنفش",
    }
    return line_colors.get(line_name, "Unknown")




def check_line(station1, station2=None) -> str:

    if station2:
        return line_lookup.get((station1, station2))

    for line, stations in lines.items():
        if station1 in stations:
            return line
        
    return None


def graph_generator() -> dict:
    graphs = {
        'lines': {f"line_{i}": Graph() for i in range(1, 8)},
        'graph_all': Graph(),
        'linetoline': {}
    }

    for i in range(1, 8):
        for j in range(1, 8):

            if len(set(lines[f'line_{i}']).intersection(lines[f'line_{j}'])) >= 1:

                graphs['linetoline'][f"line_{i}toline_{j}"] = Graph()

                line1 = lines[f'line_{i}']
                for x in range(len(line1) - 1):
                    graphs['linetoline'][f"line_{i}toline_{j}"].add_edge(line1[x], line1[x + 1], 1)
                    graphs['linetoline'][f"line_{i}toline_{j}"].add_edge(line1[x + 1], line1[x], 1)

                line2 = lines[f'line_{j}']
                for y in range(len(line2) - 1):
                    graphs['linetoline'][f"line_{i}toline_{j}"].add_edge(line2[y], line2[y + 1], 1)
                    graphs['linetoline'][f"line_{i}toline_{j}"].add_edge(line2[y + 1], line2[y], 1)

    for line_id, line in lines.items():
        for i in range(len(line) - 1):
            for graph in [graphs['lines'][line_id], graphs['graph_all']]:
                graph.add_edge(line[i], line[i + 1], 1)
                graph.add_edge(line[i + 1], line[i], 1)

    return graphs


def check_cost(distance: int) -> str:
    costs_in_city = {
        2: 33.000,
        4: 33.412,
        6: 33.824,
        8: 34.236,
        10: 34.648,
        12: 35.060,
        15: 35.678,
        18: 36.296,
        22: 37.120,
        26: 37.944,
        30: 38.768,
    }
    keys = sorted(costs_in_city.keys())
    index = bisect.bisect_left(keys, distance)
    return str(costs_in_city[keys[min(index, len(keys) - 1)]])


