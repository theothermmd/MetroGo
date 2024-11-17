from datetime import datetime
from dijkstar import find_path
from Core.libs.functions import *
base_path: str = os.path.join(os.getcwd(), "Core", "static")

graphes: dict = graph_generator()

stations = json.load(open(f"{base_path}/stations.json", "r", encoding="utf-8"))
lines = {f"line_{m}": stations["stations"][f"line_{m}"] for m in range(1, 8)}


def find_best_route(source: str, destination: str, cashe: bool = False, fastest: bool = False, time: str = f"{datetime.now().hour}:{datetime.now().minute}") -> dict:

    source: str = find_closest_word(source, stations_names)
    destination: str = find_closest_word(destination, stations_names)
    if not source or not destination:
        return {"error": "Invalid source or destination"}
    if source == destination:
        return {"error": "The ُsource and destination stations cannot be the same"}

    time = f"{datetime.now().hour}:{datetime.now().minute}"
    now = datetime.strptime(time, "%H:%M")

    start_time: datetime = now

    if not datetime.strptime("5:00", "%H:%M") < now < datetime.strptime("22:00", "%H:%M"):
        return {"route": "no service", "travel_time": "no service", "travel_cost": "no service", "travel_guide": ""}

    if cashe:
        stations_cashe: dict = json.load(open(f"{base_path}\\stations_cashe.json", "r", encoding="UTF-8"))
        if check_line(source) == check_line(destination):
            route: list = stations_cashe[check_line(source)][f'{source}-{destination}']
        else:
            route: list = stations_cashe['all'][f'{source}-{destination}']

    else:

        if check_line(source) == check_line(destination):
            graph: Graph = graphes[check_line(source)]

        elif len(set(lines[check_line(source)]).intersection(lines[check_line(destination)])) >= 1 and fastest:
            graph: Graph = graphes['linetoline'][f'{check_line(source)}to{check_line(destination)}']

        else:
            graph: Graph = graphes['graph_all']

        route: list = find_path(graph, source, destination)[0]

    corrent_line: str = check_line(route[0], route[1])
    terminal_direction: str = find_terminal_direction(corrent_line, route[0], route[1])

    overview: list = []
    travel_guide: list = []
    travel_cost: int = 0

    for i in range(len(route)):
        if i + 1 < len(route):
            if check_line(route[i], route[i + 1]) != corrent_line:

                corrent_line: str = check_line(route[i], route[i - 1])

                time: list = stations_times[corrent_line][corrent_line]["عادی"][terminal_direction][route[i]]
                now, no_schedule_flag = get_next_time(time, now)
                print(f"line : 65 -> {now} -> {route[i]}")

                corrent_line: str = check_line(route[i], route[i + 1])
                terminal_direction: str = find_terminal_direction(corrent_line, route[i], route[i + 1])

                add_overview_entry(overview, route[i], now, corrent_line, True, f"در ایستگاه {route[i]} از قطار پیاده شده و با توجه به تابلو های راهنمای به سمت {
                                   terminal_direction} وارد خط {check_line(route[i], route[i + 1]).replace('line_', '')} شوید.")

                add_travel_guide_entry("change", travel_guide, route[i], check_line(route[i], route[i + 1]).replace('line_', ''), terminal_direction)

                time: list = stations_times[corrent_line][corrent_line]["عادی"][terminal_direction][route[i]]
                now, no_schedule_flag = get_next_time(time, now)
                print(f"line : 76 -> {now} -> {route[i]}")

                add_overview_entry(overview, route[i], now, corrent_line, False, "")
                travel_cost += 2
            else:
                if i == 0:
                    add_travel_guide_entry("source", travel_guide, route[i], check_line(route[i], route[i + 1]).replace('line_', ''), terminal_direction)

                time: list = stations_times[corrent_line][corrent_line]["عادی"][terminal_direction][route[i]]
                try:
                    now, no_schedule_flag = get_next_time(time, now)
                except:
                    print(f"line : 88 -> {now} -> {route[i]}")

                if no_schedule_flag and i == 0:
                    add_overview_entry(overview, route[i], now, corrent_line, False, "")
                elif no_schedule_flag and i != 0:
                    add_overview_entry(overview, route[i], now, corrent_line, False, "در قطار پیاده شده و منتظر بمانید")
                    overview[len(overview) - 2]['message'] = "در این ایستگاه"
                else:

                    add_overview_entry(overview, route[i], now, corrent_line, False, "")
                travel_cost += 2
                if i == 0:
                    next_train = str(datetime.strptime(now, "%H:%M") - start_time)
                    next_train = str(datetime.strptime(next_train, "%H:%M:%S").minute)

        else:

            terminal_direction: str = find_terminal_direction(corrent_line, route[i - 1], route[i])

            time: list = stations_times[check_line(route[i], route[i - 1])][check_line(route[i], route[i - 1])]["عادی"][terminal_direction][route[i]]

            now, no_schedule_flag = get_next_time(time, now)
            add_overview_entry(overview, route[i], now, corrent_line, False, "")
            add_travel_guide_entry("destination", travel_guide, route[i], check_line(route[i], route[i - 1]).replace('line_', ''), terminal_direction)
            travel_cost += 2

    time = str(datetime.strptime(now, "%H:%M") - start_time).split(":")

    return {"route": overview,
            "travel_time": f"{time[0]}:{time[1]}",
            "travel_cost": check_cost(travel_cost),
            "travel_guide": travel_guide,
            "next_train": next_train}


with open(os.getcwd() + '/Core/static/stations_test.json', 'w', encoding='UTF-8') as file:
    file.write(json.dumps(find_best_route("زمزم", "دانشگاه شریف", time="12:50"), ensure_ascii=False))
