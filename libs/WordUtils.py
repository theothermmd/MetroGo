from typing import List, Optional
from rapidfuzz import process


class WordUtils:
	def __init__(self, stations_names: List[str]) -> None:
		self.stations_names = stations_names

	@staticmethod
	def correct_persian_text(text: str) -> str:

		translation_map = str.maketrans(
				{
					"ي": "ی",
					"ك": "ک",
					"ە": "ه",
					"إ": "ا",
					"ؤ": "و",
					"ء": "",
					"ة": "ه",
					"٫": ".",
					"٬": ",",
					"ّ": ""
				}
			)

		return text.translate(translation_map)

	def find_closest_word(self, input_word: str, score_threshold: int = 70) -> Optional[str]:
		result = process.extractOne(input_word, self.stations_names)
		if result is None:
			return None

		closest_match, score, _ = result
		return closest_match if score > score_threshold else None
