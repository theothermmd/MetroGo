import json
import os


def run():
	import sys

	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./")))
	sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
	import line_1
	import line_2
	import line_3
	import line_4
	import line_5
	import line_6
	import line_7
	import parand

	import libs.WordUtils as WordUtils

	line_1 = [WordUtils.WordUtils.correct_persian_text(i) for i in line_1.line_1()]
	line_2 = [WordUtils.WordUtils.correct_persian_text(i) for i in line_2.line_2()]
	line_3 = [WordUtils.WordUtils.correct_persian_text(i) for i in line_3.line_3()]
	line_4 = [WordUtils.WordUtils.correct_persian_text(i) for i in line_4.line_4()]
	line_5 = [WordUtils.WordUtils.correct_persian_text(i) for i in line_5.line_5()]
	line_6 = [WordUtils.WordUtils.correct_persian_text(i) for i in line_6.line_6()]
	line_7 = [WordUtils.WordUtils.correct_persian_text(i) for i in line_7.line_7()]
	line_parand = [WordUtils.WordUtils.correct_persian_text(i) for i in parand.parand()]

	x = {
		"stations": {
			"line_1": line_1,
			"line_parand": line_parand,
			"line_2": line_2,
			"line_3": line_3,
			"line_4": line_4,
			"line_5": line_5,
			"line_6": line_6,
			"line_7": line_7,
		}
	}

	base_path = os.path.join(os.getcwd(), "assets")

	with open(os.path.join(base_path, "stations.json"), "w", encoding="UTF-8") as file:
		file.write(json.dumps(x, ensure_ascii=False))
