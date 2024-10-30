from datetime import datetime
from dijkstar import Graph
import json
import os
import unicodedata
from fuzzywuzzy import process
import bisect






base_path = os.path.join(os.getcwd(), "Core", "static")

# Load data
stations_times = {f"line_{i}": json.load(open(f"{base_path}/stations_{i}.json", "r", encoding="UTF-8")) for i in range(1, 8)}

stations = json.load(open(f"{base_path}/stations.json", "r", encoding="utf-8"))

# Collect station names
stations_names = []
lines = {f"line_{m}": stations["stations"][f"line_{m}"] for m in range(1, 8)}
for line in lines.values():
    stations_names.extend(line)

# Define terminals for each line
terminals = {line_name: [line[0], line[-1]] for line_name, line in lines.items()}

line_lookup = {}
for line, stations in lines.items(): 

    for i in range(len(stations) - 1):
        line_lookup[(stations[i], stations[i + 1])] = line
        line_lookup[(stations[i + 1], stations[i])] = line


def find_closest_word(input_word, word_list) -> str:

    closest_match, score = process.extractOne(input_word, word_list)
    return closest_match if score > 70 else None

def find_terminal_direction(line, current_station, next_station) -> str:

    if lines[line].index(current_station) < lines[line].index(next_station):
        return terminals[line][1]
    else:
        return terminals[line][0]
    
def get_next_time(station_times, current_time):
    
    if not isinstance(current_time, datetime):
        current_time = datetime.strptime(current_time, "%H:%M")
    flag = False
    for time_str in station_times:

        if time_str == "None" or time_str == None or time_str == "" or time_str == "none":
            flag = True     
            continue

        if time_str and time_str != "None" and datetime.strptime(time_str, "%H:%M") > current_time:
            
            if len(str(datetime.strptime(time_str, '%H:%M').minute)) == 1 :
                return f"{datetime.strptime(time_str, '%H:%M').hour}:0{datetime.strptime(time_str, '%H:%M').minute}" , flag
            else :
                return f"{datetime.strptime(time_str, "%H:%M").hour}:{datetime.strptime(time_str, '%H:%M').minute}" , flag
    return None
def add_overview_entry(overview, station_name, time, line_name, is_line_change, message="") -> None:

    overview.append({
        "station_name": station_name,
        "time": time,
        "color": get_line_color(line_name),
        "is_line_change": is_line_change,
        "message": message
    })
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


def normalize_str(s) -> str:

    return unicodedata.normalize("NFC", s).strip()


        
def check_line(station1, station2=None) -> str :
    if station2:
        return line_lookup.get((station1, station2))
    

    for line, stations in lines.items():
        if station1 in stations:
            return line
    return None 

def graph_generator() -> dict:
    graph_all : Graph = Graph()
    graph_line_1 : Graph = Graph()
    graph_line_2 : Graph = Graph()
    graph_line_3 : Graph = Graph()
    graph_line_4 : Graph = Graph()
    graph_line_5 : Graph = Graph()
    graph_line_6 : Graph = Graph()
    graph_line_7 : Graph = Graph()
    graph_lines = [graph_line_1 , graph_line_2 , graph_line_3 , graph_line_4 , graph_line_5 , graph_line_6 , graph_line_7]

    for j , graph in zip(range(1, 8) , graph_lines):
        for i in range(len(lines[f"line_{j}"]) - 1):
            graph.add_edge(lines[f"line_{j}"][i], lines[f"line_{j}"][i + 1], 1)
            graph.add_edge(lines[f"line_{j}"][i + 1], lines[f"line_{j}"][i], 1)

            
    for line in lines.values():
            for i in range(len(line) - 1):
                graph_all.add_edge(line[i], line[i + 1], 1)
                graph_all.add_edge(line[i + 1], line[i], 1)
    return {'graph_all' : graph_all , 'line_1' : graph_line_1 , 'line_2' : graph_line_2 , 'line_3' : graph_line_3, 'line_4' : graph_line_4 , 'line_5' : graph_line_5 , 'line_6' : graph_line_6 , 'line_7' : graph_line_7 ,}


def check_cost(distance : int) -> str :
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

    if index == len(keys):  
        return str((costs_in_city[keys[-1]]))
    elif distance == keys[index]: 
        return str((costs_in_city[keys[index]]))
    else: 
        return str((costs_in_city[keys[index]]))


def add_travel_guide_entry(flag , travel_guide, station_name, line_name , terminal) -> None:
    if flag == "source".lower(): 
        travel_guide.append(f"در ایستگاه {station_name} وارد خط {line_name} شوید و به سمت {terminal} سوار مترو شوید.")
    elif flag == "change".lower():
        travel_guide.append(f"در ایستگاه {station_name} از مترو پیاده شوید. سپس وارد خط {line_name} شده و به سمت {terminal} سوار مترو شوید.")
    elif flag == "destination".lower():
        travel_guide.append(f"در ایستگاه {station_name} از مترو پیاده شوید و از ایستگاه خارج شوید. ")