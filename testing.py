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



# season_logs = d['gamelog_url_list']
# for season_log in season_logs:
#     curr_season_df = bc.dfFromGameLogURL(season_log)
#     game_num = 0
#     playoff_index = -1
#     prev_row_index = -1
#     for index, row in curr_season_df.iterrows():
#         curr_game = int(row["G"])
#         if curr_game >= game_num:
#             game_num += 1
#         else:
#             playoff_index = prev_row_index + 1
#             break
#         prev_row_index = index
#     regular_season_df = (curr_season_df.iloc[:playoff_index]).to_dict()
#     playoff_df = (curr_season_df.iloc[playoff_index:]).to_dict()
#     print(regular_season_df)
