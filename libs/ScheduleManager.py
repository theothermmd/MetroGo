from datetime import datetime
from typing import List, Tuple, Optional, Union


class ScheduleManager:
	@staticmethod
	def is_time_valid(time_str: Optional[str]) -> bool:
		return time_str not in [None, "", "None", "none"]

	@staticmethod
	def get_next_time(station_times: List[str], current_time: Union[str, datetime]) -> Tuple[Optional[str], bool]:
		if isinstance(current_time, str):
			try:
				current_time_dt = datetime.strptime(current_time, "%H:%M")
			except ValueError as e:
				raise ValueError(f"Invalid current_time format: {current_time}") from e
		else:
			current_time_dt = current_time

		no_schedule_flag = False

		for time_str in station_times:
			if not ScheduleManager.is_time_valid(time_str):
				no_schedule_flag = True
				continue

			try:
				next_time = datetime.strptime(time_str, "%H:%M")
			except ValueError:
				no_schedule_flag = True
				continue

			if next_time > current_time_dt:
				formatted_time = next_time.strftime("%H:%M")
				return formatted_time, no_schedule_flag

		return None, no_schedule_flag
