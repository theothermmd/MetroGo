import os
import json
from dijkstar import Graph, find_path
base_path = os.path.join(os.getcwd(), "Core", "static")

stations = json.load(open(f"{base_path}/stations.json", "r", encoding="utf-8"))


stations_names = []
lines = {f"line_{m}": stations["stations"][f"line_{m}"] for m in range(1, 8)}
for line in lines.values():
    stations_names.extend(line)


lines = {f"line_{m}": stations["stations"][f"line_{m}"] for m in range(1, 8)}


def graph_generator() -> dict:
    graph_all: Graph = Graph()
    graph_line_1: Graph = Graph()
    graph_line_2: Graph = Graph()
    graph_line_3: Graph = Graph()
    graph_line_4: Graph = Graph()
    graph_line_5: Graph = Graph()
    graph_line_6: Graph = Graph()
    graph_line_7: Graph = Graph()
    graph_lines = [graph_line_1, graph_line_2, graph_line_3,
                   graph_line_4, graph_line_5, graph_line_6, graph_line_7]

    for j, graph in zip(range(1, 8), graph_lines):
        for i in range(len(lines[f"line_{j}"]) - 1):
            graph.add_edge(lines[f"line_{j}"][i], lines[f"line_{j}"][i + 1], 1)
            graph.add_edge(lines[f"line_{j}"][i + 1], lines[f"line_{j}"][i], 1)

    for line in lines.values():
        for i in range(len(line) - 1):
            graph_all.add_edge(line[i], line[i + 1], 1)
            graph_all.add_edge(line[i + 1], line[i], 1)
    return {'graph_all': graph_all, 'line_1': graph_line_1, 'line_2': graph_line_2, 'line_3': graph_line_3, 'line_4': graph_line_4, 'line_5': graph_line_5, 'line_6': graph_line_6, 'line_7': graph_line_7, }


graphes = graph_generator()

all = {}

for i in range(1, 8):
    all[f'line_{i}'] = {}
    for j, n in zip(lines[f'line_{i}'], reversed(lines[f'line_{i}'])):
        if j == n:
            break
        else:
            all[f'line_{i}'][f'{
                j}-{n}'] = find_path(graphes[f'line_{i}'], j, n)[0]

all["all"] = {}


for m in stations_names:
    for x in stations_names:
        if m != x:
            all["all"][f'{m}-{x}'] = find_path(graphes["graph_all"], m, x)[0]


with open(os.getcwd() + '\\Core\\cashe\\stations_cashe.json', 'w', encoding='UTF-8') as file:
    file.write(json.dumps(all, ensure_ascii=False))
