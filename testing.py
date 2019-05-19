import basketballCrawler as bc
import json
import ast
# players_url_list = bc.getAllPlayerNamesAndURLS()
# players = bc.buildSpecificPlayerDictionary(players_url_list)
# bc.savePlayerDictionary(players, 'data.json')

json_object = json.load(open("data.json"))
kobe = json_object['Kobe Bryant']
json_acceptable_string = kobe.replace("'", "\"")
d = json.loads(json_acceptable_string)
sample_url = d['gamelog_url_list'][0]
print(bc.dfFromGameLogURL(sample_url))
# bc.dfFromGameLogURL(kobe['gamelog_url_list'][0])
