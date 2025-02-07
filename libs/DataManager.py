import json
from pathlib import Path
from collections import defaultdict


class DataManager:
	def __init__(self) -> None:
		assets_path = Path.cwd() / "assets"

		stations_file_path = assets_path / "stations.json"
		if not stations_file_path.exists():
			raise RuntimeError("Missing stations.json")
		try:
			self.stations = json.loads(stations_file_path.read_text(encoding="utf-8"))
		except Exception as e:
			raise RuntimeError(f"Error reading stations.json: {e}") from e

		time_lines_dir = assets_path / "time_lines"
		if not time_lines_dir.exists():
			raise RuntimeError("Missing time_lines directory")

		self.stations_times = {}
		for json_file in time_lines_dir.glob("*.json"):
			line_name = json_file.stem
			try:
				self.stations_times[line_name] = json.loads(json_file.read_text(encoding="utf-8"))
			except Exception as e:
				raise RuntimeError(f"Error reading {json_file.name}: {e}") from e

		self.stations_names = [station for stations in self.stations["stations"].values() for station in stations]

		self.terminals = {line_name: [stations[0], stations[-1]] for line_name, stations in self.stations["stations"].items()}

		self.line_lookup = {}
		for line, stations in self.stations["stations"].items():
			for station_a, station_b in zip(stations, stations[1:]):
				self.line_lookup[(station_a, station_b)] = line
				self.line_lookup[(station_b, station_a)] = line

		stations_line = defaultdict(list)
		for line, stations in self.stations["stations"].items():
			for station in stations:
				if line not in stations_line[station]:
					stations_line[station].append(line)
		self.stations_line = dict(stations_line)
