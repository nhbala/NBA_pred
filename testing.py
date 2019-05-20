import basketballCrawler as bc
import json
import ast
import pandas as pd
# players_url_list = bc.getAllPlayerNamesAndURLS()
# players = bc.buildSpecificPlayerDictionary(players_url_list)
# bc.savePlayerDictionary(players, 'data.json')

json_object = json.load(open("data.json"))
kobe = json_object['Kobe Bryant']
json_acceptable_string = kobe.replace("'", "\"")
d = json.loads(json_acceptable_string)
main_page = d['overview_url']
print(bc.getoverView(main_page))
