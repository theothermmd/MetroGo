import json
import os
import Core.scrapers.line_1
import Core.scrapers.line_2
import Core.scrapers.line_3
import Core.scrapers.line_4
import Core.scrapers.line_5
import Core.scrapers.line_6
import Core.scrapers.line_7
import Core.core
os.system('cls')
print("Running...")

x = {'stations' : {'line_1' : Core.scrapers.line_1.line_1() , 'line_2' : Core.scrapers.line_2.line_2() , 'line_3' : Core.scrapers.line_3.line_3() , 
                   'line_4' : Core.scrapers.line_4.line_4() , 'line_5' : Core.scrapers.line_5.line_5() , 'line_6' : Core.scrapers.line_6.line_6() ,
                   'line_7' : Core.scrapers.line_7.line_7()} }
with open(os.getcwd() + '/Core/static/stations.json', 'w', encoding='UTF-8') as file:
        file.write(json.dumps(x, ensure_ascii=False))

with open( os.getcwd() + "/Core/static/stations.json", "r", encoding="utf-8" ) as json_config_file: 
    stations = json.load(json_config_file)

print("Finish.")

