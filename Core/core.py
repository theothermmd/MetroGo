from datetime import datetime
from dijkstar import find_path
from Core.libs.functions import *



graphes = graph_generator()


def find_best_route(source, destination) -> dict:

    source: str = find_closest_word(source, stations_names)
    destination: str = find_closest_word(destination, stations_names)
    if not source or not destination:
        return {"error": "Invalid source or destination"}
    if source == destination:
        return {"error": "The ُsource and destination stations cannot be the same"}
    if check_line(source) == check_line(destination):
        graph = graphes[check_line(source)]

    else:
        graph = graphes['graph_all']

    # now = datetime.strptime(f"{datetime.now().hour}:{ datetime.now().minute}", "%H:%M")
    now = datetime.strptime("7:40", "%H:%M")
    start_time: datetime = now

    if not datetime.strptime("5:00", "%H:%M") < now < datetime.strptime("22:00", "%H:%M"):
        return {"route": "no service", "travel_time": "no service", "travel_cost": "no service", "travel_guide": ""}

    route: list = find_path(graph, source, destination)[0]
    corrent_line: str = check_line(route[0], route[1])
    terminal_direction: str = find_terminal_direction(
        corrent_line, route[0], route[1])

    overview: list = []
    travel_guide = []
    travel_cost = 0

    for i in range(len(route)):
        if i + 1 < len(route):
            if check_line(route[i], route[i + 1]) != corrent_line:
                corrent_line: str = check_line(route[i], route[i - 1])
                time: list = stations_times[corrent_line][corrent_line]["عادی"][terminal_direction][route[i]]
                now, flag = get_next_time(time, now)

                corrent_line: str = check_line(route[i], route[i + 1])
                terminal_direction: str = find_terminal_direction(
                    corrent_line, route[i], route[i + 1])
                add_overview_entry(overview, route[i], now, corrent_line, True, f"در ایستگاه {route[i]} از قطار پیاده شده و با توجه به تابلو های راهنمای به سمت {
                                   terminal_direction} وارد خط {check_line(route[i], route[i + 1]).replace('line_', '')} شوید.")
                add_travel_guide_entry("change", travel_guide, route[i], check_line(
                    route[i], route[i + 1]).replace('line_', ''), terminal_direction)
                time: list = stations_times[corrent_line][corrent_line]["عادی"][terminal_direction][route[i]]
                now, flag = get_next_time(time, now)
                add_overview_entry(
                    overview, route[i], now, corrent_line, False, "")
                travel_cost += 2
            else:
                if i == 0:
                    add_travel_guide_entry("source", travel_guide, route[i], check_line(
                        route[i], route[i + 1]).replace('line_', ''), terminal_direction)
                corrent_line: str = check_line(route[i], route[i + 1])

                time: list = stations_times[corrent_line][corrent_line]["عادی"][terminal_direction][route[i]]

                try:
                    now, flag = get_next_time(time, now)
                except Exception as e:
                    print(f"line : {corrent_line} , ter : {terminal_direction} , station : {
                          route[i]} , dest : {terminal_direction} , line : {corrent_line} .e : {e} ")
                if flag and i == 0:
                    add_overview_entry(
                        overview, route[i], now, corrent_line, False, "")
                elif flag and i != 0:
                    add_overview_entry(
                        overview, route[i], now, corrent_line, False, "در قطار پیاده شده و منتظر بمانید")
                    overview[len(overview) - 2]['message'] = "در این ایستگاه"
                else:

                    add_overview_entry(
                        overview, route[i], now, corrent_line, False, "")
                travel_cost += 2
                if i == 0:
                    first = str(datetime.strptime(now, "%H:%M") - start_time)



        else:

            terminal_direction: str = find_terminal_direction(
                corrent_line, route[i - 1], route[i])

            time: list = stations_times[check_line(route[i], route[i - 1])][check_line(
                route[i], route[i - 1])]["عادی"][terminal_direction][route[i]]

            now, flag = get_next_time(time, now)
            add_overview_entry(
                overview, route[i], now, corrent_line, False, "")
            add_travel_guide_entry("destination", travel_guide, route[i], check_line(
                route[i], route[i - 1]).replace('line_', ''), terminal_direction)
            travel_cost += 2

    time = str(datetime.strptime(now, "%H:%M") - start_time).split(":")

    return {"route": overview, "travel_time": f"{time[0]}:{time[1]}", "travel_cost": check_cost(travel_cost), "travel_guide": travel_guide , "first" : str(datetime.strptime(first, "%H:%M:%S").minute)}
