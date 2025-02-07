from typing import Dict, List, Optional


class LineManager:
	def __init__(
		self, line_lookup: Dict[tuple, str], terminals: Dict[str, List[str]], stations: Dict[str, Dict[str, List[str]]]
	) -> None:
		"""
		Initializes the LineManager with provided data.

		:param line_lookup: A dictionary mapping tuples of (station1, station2) to a line name.
		:param terminals: A dictionary mapping each line to its terminal stations [start, end].
		:param stations: A dictionary with stations data, e.g., {"stations": {line: [station1, station2, ...]}}.
		"""
		self.line_lookup = line_lookup
		self.terminals = terminals
		self.stations = stations

	def get_line_for_station(self, station1: str, station2: str) -> Optional[str]:
		"""
		Returns the line connecting the two given stations.

		:param station1: Name of the first station.
		:param station2: Name of the second station.
		:return: The line name if found, otherwise None.
		"""
		return self.line_lookup.get((station1, station2))

	def find_terminal_direction(self, line: str, current_station: str, next_station: str) -> str:
		"""
		Determines the terminal direction for the given line based on the order of stations.

		:param line: The line name.
		:param current_station: The current station name.
		:param next_station: The next station name.
		:return: The terminal station in the direction of travel.
		:raises ValueError: If the line or one of the stations is not found.
		"""
		line_stations = self.stations["stations"].get(line)
		if line_stations is None:
			raise ValueError(f"Line '{line}' does not exist in stations data.")

		try:
			current_index = line_stations.index(current_station)
			next_index = line_stations.index(next_station)
		except ValueError as e:
			raise ValueError("Current station or next station not found in the list of stations.") from e

		# اگر ایندکس ایستگاه فعلی کمتر از ایندکس ایستگاه بعدی باشد، به سمت انتهای خط حرکت می‌کنیم.
		if current_index < next_index:
			return self.terminals[line][1]
		else:
			return self.terminals[line][0]

	@staticmethod
	def get_line_color(line_name: str) -> str:
		"""
		Returns the color of the given line.

		:param line_name: The line name.
		:return: The color associated with the line or "Unknown" if not defined.
		"""
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
