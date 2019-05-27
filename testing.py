import basketballCrawler as bc
import json
import ast
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from player import Player, getSoupFromURL
from time import sleep

# players_url_list = bc.getAllPlayers()
# bc.savePlayerDictionary(players_url_list, 'data.json')

final_dict = {}
json_object = json.load(open("result.json"))
for curr_object in json_object:
    final_dict[curr_object[0]] = curr_object[1]

with open('finaldict.json', 'w') as fp:
         json.dump(final_dict, fp)







def getovHelper(table_soup):
    try:
        table = table_soup.find('table')
        averages = table.find_all("tbody")
        rows = averages[0].findAll('tr')
        years = []
        for row in rows:
            year_html = row.find('a')
            if year_html == None:
                years.append(0)
            else:
                year = year_html.getText()
                years.append(year)
        rows = [r for r in rows if len(r.findAll('td')) > 0]
        parsed_rows = [[col.getText() for col in row.findAll('td')] for row in rows]
        parsed_table = [row for row in parsed_rows if row[0] != ""]
        for index in range(len(parsed_table)):
            curr_year = years[index]
            (parsed_table[index]).insert(0, curr_year)
        return parsed_table
    except:
        return []



def getoverView(url_tup):
    print(url_tup[0])


    sleep(2)
    try:
        glsoup = getSoupFromURL(url_tup[1])
        id_lst = ["all_per_game", "all_totals", "all_per_minute", "all_per_poss", "all_advanced", "all_shooting", "all_pbp", "all_playoffs_per_game", "all_playoffs_totals", "all_playoffs_per_minute", "all_playoffs_per_poss", "all_playoffs_advanced", "all_playoffs_shooting", "all_playoffs_pbp", "all_all_salaries"]
        final_dict = {}
        for curr_id in id_lst:
            curr_div = glsoup.find("div", {"id": curr_id})
            if curr_div != None:
                div = curr_div.find("div", {"class": "overthrow table_container"})
                table_header_lst = div.find("thead")
                th_lst = table_header_lst.find_all("tr")
                final_th_header = th_lst[-1]
                header_lst = []
                th_stuff = final_th_header.find_all("th")
                for th_thing in th_stuff:
                    curr_val = th_thing.get_text()
                    header_lst.append(curr_val)
                curr_table = getovHelper(div)
                final_table = curr_table
                final_table.insert(0, header_lst)
                final_dict[curr_id] = final_table
        sleep(2)

        return (url_tup[0], final_dict)
    except:
        return (url_tup[0], {})

def run_script():
    json_object = json.load(open("data.json"))
    final_list = []
    for name in json_object:
        player = json_object[name]
        json_acceptable_string = player.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        main_page = d['overview_url']
        final_list.append((name, main_page))

    final_lst = final_list



    with ProcessPoolExecutor(max_workers=4) as executor:
        future_results = [executor.submit(getoverView, url) for url in final_lst]
        result_lst = []
        for results in as_completed(future_results):
            result_lst.append(results.result())
        with open('result.json', 'w') as fp:
            json.dump(result_lst, fp)
