from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List, Optional, Tuple, Any


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from libs.DataManager import DataManager
from libs.LineManager import LineManager
from libs.Routing import Routing
from libs.ScheduleManager import ScheduleManager
from libs.TravelInfo import TravelInfo
from libs.WordUtils import WordUtils


data_manager = DataManager()
word_utils = WordUtils(data_manager.stations_names)
line_manager = LineManager(data_manager.line_lookup, data_manager.terminals, data_manager.stations)
routing = Routing(data_manager.stations, data_manager.stations_line)

METRO_START = datetime.strptime("05:00", "%H:%M")
METRO_END = datetime.strptime("23:00", "%H:%M")
DISTANCE_STEP = 2


def parse_time(time_str: str) -> datetime:
	return datetime.strptime(time_str, "%H:%M")


def format_duration(duration: timedelta) -> str:
	total_minutes = int(duration.total_seconds() // 60)
	hours, minutes = divmod(total_minutes, 60)
	return f"{hours:02}:{minutes:02}"


def find_best_route(source: str, destination: str, type_day: str, current_time_str: Optional[str] = None) -> Dict[str, Any]:
	if source == destination:
		return {"status": True, "isrouting": False, "message": "The origin and destination stations cannot be the same."}

	if type_day not in ["عادی", "پنجشنبه", "جمعه"]:
		return {"status": True, "isrouting": False, "message": "Days of the week are not valid."}

	source_corrected = word_utils.find_closest_word(input_word=source)
	destination_corrected = word_utils.find_closest_word(input_word=destination)

	if source_corrected is None or destination_corrected is None:
		if source_corrected is None and destination_corrected is None:
			message = "The names of the origin and destination stations are not valid."
		elif source_corrected is None:
			message = "The origin station name is not valid."
		else:
			message = "The destination station name is not valid."

		return {"status": True, "isrouting": False, "message": message}

	current_time = parse_time(current_time_str) if current_time_str else datetime.now()
	if not (METRO_START < current_time < METRO_END):
		return {"status": True, "isrouting": False, "message": "The metro is not operating."}

	start_time = current_time

	route: List[str] = routing.find_fastest_route(source=source_corrected, destination=destination_corrected)
	if not route or len(route) < 2:
		return {"status": True, "isrouting": False, "message": "No valid route found."}

	current_line: str = line_manager.get_line_for_station(route[0], route[1])
	terminal_direction: str = line_manager.find_terminal_direction(current_line, route[0], route[1])
	overview: List[Dict[str, str, str, bool, str]] = []
	travel_guide: List[str] = []
	travel_distance: int = 0
	next_train: Optional[str] = None

	def update_time_for_station(
		line: str, station: str, direction: str, current_time_val: datetime
	) -> Tuple[Optional[datetime], bool]:
		time_list = data_manager.stations_times[line][line][type_day][direction][station]

		next_time_str, flag = ScheduleManager.get_next_time(time_list, current_time_val)
		if next_time_str is None:
			return None, flag
		return parse_time(next_time_str), flag

	for i in range(len(route)):
		if i < len(route) - 1:
			next_line = line_manager.get_line_for_station(route[i], route[i + 1])

			if next_line != current_line:
				updated_time, flag = update_time_for_station(current_line, route[i], terminal_direction, current_time)
				if updated_time is None:
					return {"status": True, "isrouting": False, "message": "You will not reach your destination station."}
				current_time = updated_time

				TravelInfo.add_overview_entry(
					overview,
					route[i],
					current_time.strftime("%H:%M"),
					current_line,
					True,
					f"در ایستگاه {route[i]} از قطار پیاده شده و به سمت {terminal_direction} جهت تغییر خط به {next_line.replace('line_', '')} اقدام کنید.",
				)
				TravelInfo.add_travel_guide_entry(
					"change",
					travel_guide,
					route[i],
					next_line.replace("line_", ""),
					terminal_direction,
				)

				current_line = next_line
				terminal_direction = line_manager.find_terminal_direction(current_line, route[i], route[i + 1])
				updated_time, flag = update_time_for_station(current_line, route[i], terminal_direction, current_time)
				if updated_time is None:
					return {"status": True, "isrouting": False, "message": "You will not reach your destination station."}
				current_time = updated_time
				TravelInfo.add_overview_entry(overview, route[i], current_time.strftime("%H:%M"), current_line, False, "")
				travel_distance += DISTANCE_STEP

			else:
				if i == 0:
					TravelInfo.add_travel_guide_entry(
						"source",
						travel_guide,
						route[i],
						next_line.replace("line_", ""),
						terminal_direction,
					)
				current_line = next_line
				updated_time, flag = update_time_for_station(current_line, route[i], terminal_direction, current_time)
				if updated_time is None:
					return {"status": True, "isrouting": False, "message": "You will not reach your destination station."}
				current_time = updated_time

				if flag and i > 0:
					TravelInfo.add_overview_entry(
						overview,
						route[i],
						current_time.strftime("%H:%M"),
						current_line,
						False,
						"در قطار پیاده شده و منتظر بمانید",
					)

					if len(overview) >= 2:
						overview[-2]["message"] = "در این ایستگاه"
				else:
					TravelInfo.add_overview_entry(overview, route[i], current_time.strftime("%H:%M"), current_line, False, "")
				travel_distance += DISTANCE_STEP

				if i == 0:
					wait_duration = current_time - start_time
					next_train = str(wait_duration.seconds // 60)

		else:
			terminal_direction = line_manager.find_terminal_direction(current_line, route[i - 1], route[i])

			dest_line = line_manager.get_line_for_station(route[i], route[i - 1])
			time_list = data_manager.stations_times[dest_line][dest_line][type_day][terminal_direction][route[i]]
			updated_time, flag = ScheduleManager.get_next_time(time_list, current_time)
			if updated_time is None:
				return {"status": True, "isrouting": False, "message": "You will not reach your destination station."}
			current_time = parse_time(updated_time) if isinstance(updated_time, str) else updated_time
			TravelInfo.add_overview_entry(overview, route[i], current_time.strftime("%H:%M"), current_line, False, "")
			TravelInfo.add_travel_guide_entry(
				"destination",
				travel_guide,
				route[i],
				dest_line.replace("line_", ""),
				terminal_direction,
			)
			travel_distance += DISTANCE_STEP

	travel_duration = format_duration(current_time - start_time)
	cost = TravelInfo.check_cost(travel_distance)

	return {
		"status": True,
		"isrouting": True,
		"fail": False,
		"route": overview,
		"travel_duration": travel_duration,
		"travel_distance": cost,
		"travel_guide": travel_guide,
		"next_train": next_train,
		"arrival_time": current_time.strftime("%H:%M"),
	}
