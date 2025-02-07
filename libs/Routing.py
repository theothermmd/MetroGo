from dijkstar import Graph, find_path
from typing import Dict, List, Optional, Any


class Routing:
	def __init__(self, stations_file: Dict[str, Any], stations_line: Dict[str, List[str]]) -> None:
		self.stations_file = stations_file
		self.stations_line = stations_line

		self.graph: Dict[str, Any] = {"lines": {}, "linetoline": {}, "all": Graph()}

		for line, stations in stations_file["stations"].items():
			line_graph = Graph()
			for station_a, station_b in zip(stations, stations[1:]):
				line_graph.add_edge(station_a, station_b, 1)
				line_graph.add_edge(station_b, station_a, 1)
			self.graph["lines"][line] = line_graph

		for line, stations in stations_file["stations"].items():
			self.graph["linetoline"][line] = {}
			for other_line, other_stations in stations_file["stations"].items():
				if line == other_line:
					continue

				if set(stations).intersection(other_stations):
					linetoline_graph = Graph()

					for station_a, station_b in zip(stations, stations[1:]):
						linetoline_graph.add_edge(station_a, station_b, 1)
						linetoline_graph.add_edge(station_b, station_a, 1)

					for station_a, station_b in zip(other_stations, other_stations[1:]):
						linetoline_graph.add_edge(station_a, station_b, 1)
						linetoline_graph.add_edge(station_b, station_a, 1)
					self.graph["linetoline"][line][other_line] = linetoline_graph

		all_graph = Graph()
		for stations in stations_file["stations"].values():
			for station_a, station_b in zip(stations, stations[1:]):
				all_graph.add_edge(station_a, station_b, 1)
				all_graph.add_edge(station_b, station_a, 1)
		self.graph["all"] = all_graph

	@staticmethod
	def find_intersection(arr1: List[str], arr2: List[str]) -> Optional[List[str]]:
		intersection = list(set(arr1) & set(arr2))
		return intersection if intersection else None

	def find_fastest_route(self, source: str, destination: str) -> List[str]:
		common_lines = self.find_intersection(self.stations_line[source], self.stations_line[destination])

		if common_lines is not None and len(common_lines) == 1:
			line = common_lines[0]
			return find_path(self.graph["lines"][line], source, destination)[0]

		else:
			src_lines = self.stations_line[source]
			dest_lines = self.stations_line[destination]

			if len(src_lines) == 1 and len(dest_lines) == 1:
				src_line = src_lines[0]
				dest_line = dest_lines[0]
				if src_line in self.graph["linetoline"] and dest_line in self.graph["linetoline"][src_line]:
					return find_path(self.graph["linetoline"][src_line][dest_line], source, destination)[0]

			for src_line in src_lines:
				if src_line in self.graph["linetoline"]:
					for dest_line in dest_lines:
						if dest_line in self.graph["linetoline"][src_line]:
							return find_path(self.graph["linetoline"][src_line][dest_line], source, destination)[0]

			return find_path(self.graph["all"], source, destination)[0]
