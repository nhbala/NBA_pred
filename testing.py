import basketballCrawler as bc
import json
import ast
import pandas as pd
# players_url_list = bc.getAllPlayerNamesAndURLS()
# players = bc.buildSpecificPlayerDictionary(players_url_list)
# bc.savePlayerDictionary(players, 'data.json')

# json_object = json.load(open("data.json"))
# for x in json_object:
#     print(x)
json_acceptable_string = kobe.replace("'", "\"")
d = json.loads(json_acceptable_string)
main_page = d['overview_url']
table = bc.getoverView(main_page)
with open('result.json', 'w') as fp:
    json.dump(table, fp)
