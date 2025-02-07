import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from Core.core import find_best_route
import unittest
import libs.DataManager as DataManager
import scrapers.run as run

run.run()


class TestMathFunctions(unittest.TestCase):
	def test_core(self):
		stations_names = DataManager.DataManager().stations_names
		stations_names_reverse = stations_names[::-1]
		for origin, destination in zip(stations_names, stations_names_reverse):
			if origin != destination:
				with self.subTest(origin=origin, destination=destination):
					result = find_best_route(origin, destination, "5:30", "عادی")
					result = find_best_route(origin, destination, "22:00", "عادی")
					self.assertTrue(result["status"])

				with self.subTest(origin=origin, destination=destination):
					result = find_best_route(origin, destination, "5:30", "عادی")
					result = find_best_route(origin, destination, "22:00", "عادی")
					self.assertTrue(result["status"])

				with self.subTest(origin=origin, destination=destination):
					result = find_best_route(origin, destination, "5:30", "عادی")
					result = find_best_route(origin, destination, "22:00", "عادی")
					self.assertTrue(result["status"])


if __name__ == "__main__":
	unittest.main()
