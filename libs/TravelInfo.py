from libs.LineManager import LineManager
import bisect
from typing import List, Dict, Any


class TravelInfo:
	@staticmethod
	def add_overview_entry(
		overview: List[Dict[str, Any]], station_name: str, time: str, line_name: str, is_line_change: bool, message: str = ""
	) -> None:
		overview.append(
			{
				"station_name": station_name,
				"time": time,
				"color": LineManager.get_line_color(line_name),
				"is_line_change": is_line_change,
				"message": message,
			}
		)

	@staticmethod
	def add_travel_guide_entry(flag: str, travel_guide: List[str], station_name: str, line_name: str, terminal: str) -> None:
		flag_lower = flag.lower()
		if flag_lower == "source":
			travel_guide.append(f"در ایستگاه {station_name} وارد خط {line_name} شوید و به سمت {terminal} سوار مترو شوید.")
		elif flag_lower == "change":
			travel_guide.append(
				f"در ایستگاه {station_name} از مترو پیاده شوید. سپس وارد خط {line_name} شده و به سمت {terminal} سوار مترو شوید."
			)
		elif flag_lower == "destination":
			travel_guide.append(f"در ایستگاه {station_name} از مترو پیاده شوید و از ایستگاه خارج شوید.")

	@staticmethod
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
		chosen_key = keys[min(index, len(keys) - 1)]
		return str(costs_in_city[chosen_key])
