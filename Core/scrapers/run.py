import json
import os

import line_1
import line_2
import line_3
import line_4
import line_5
import line_6
import line_7

os.system('cls')
print("Running...")

x = {'stations' : {'line_1' : line_1.line_1() , 'line_2' : line_2.line_2() , 'line_3' : line_3.line_3() , 
                   'line_4' : line_4.line_4() , 'line_5' : line_5.line_5() , 'line_6' : line_6.line_6() ,
                   'line_7' : line_7.line_7()} }
with open(os.getcwd() + '/Core/static/stations.json', 'w', encoding='UTF-8') as file:
        file.write(json.dumps(x, ensure_ascii=False))

with open( os.getcwd() + "/Core/static/stations.json", "r", encoding="utf-8" ) as json_config_file: 
    stations = json.load(json_config_file)

print("Finish.")

