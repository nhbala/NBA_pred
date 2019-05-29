import basketballCrawler as bc
import json
import ast
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from player import Player, getSoupFromURL
from time import sleep
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from kneed import DataGenerator, KneeLocator


PER_GAME_REG_OPTIMAL_K = 6

def create_final_dict():
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

def create_modified_dict():
    json_object = json.load(open("finaldict.json"))
    final_dict = {}
    for curr_name in json_object:
        curr_person_values = json_object[curr_name]
        modified_dict = {}
        for topic in curr_person_values:
            curr_values = curr_person_values[topic]
            curr_value_header = curr_values[0]
            curr_actual_values = curr_values[1:]
            for category_index in range(len(curr_value_header)):
                header_val = (curr_value_header[category_index]).replace('\xa0', '')
                for row_index in range(len(curr_actual_values)):
                    if len(curr_value_header) == len(curr_actual_values[row_index]):
                        curr_row_value = curr_actual_values[row_index][category_index]
                        if header_val == '' and curr_row_value == '':
                            curr_actual_values[row_index][category_index] = "remove"
                            curr_value_header[category_index] = "remove"
                        if header_val != '' and curr_row_value == '':
                            curr_actual_values[row_index][category_index] = "N/A"
            modified_matrix = [curr_value_header] + curr_actual_values
            modified_matrix = [[element for element in row if element != 'remove'] for row in modified_matrix]
            modified_dict[topic] = modified_matrix
        final_dict[curr_name] = modified_dict
    with open('modified_dict.json', 'w') as fp:
        json.dump(final_dict, fp)

def final_dict_cleaning():
    json_object = json.load(open("modified_dict.json"))
    final_dict = {}
    for person in json_object:
        person_values = json_object[person]
        modified_dict = {}
        for topic in person_values:
            curr_values = person_values[topic]
            correct_len = len(curr_values[0])
            index_to_delete = []
            for index in range(len(curr_values)):
                if len(curr_values[index]) != correct_len:
                    index_to_delete.append(index)
            index_to_delete.sort(reverse = True)
            for delete_index in index_to_delete:
                del curr_values[delete_index]
            modified_dict[topic] = curr_values
        final_dict[person] = modified_dict
    with open('allcleaned_data.json', 'w') as fp:
        json.dump(final_dict, fp)

def get80sdata():
    json_object = json.load(open("allcleaned_data.json"))
    names_lst = []
    for person in json_object:
        person_stuff = json_object[person]
        for topic in person_stuff:
            curr_values = person_stuff[topic]
            if len(curr_values) >= 2:
                if curr_values[1][0] != 0:
                    curr_year = curr_values[1][0]
                    if "-" in curr_year:
                        year_array = curr_year.split("-")
                        if int(year_array[0]) >= 1979:
                             names_lst.append(person)
                             break
    final_dict = {}
    for name in names_lst:
        final_dict[name] = json_object[name]
    with open('post80salldata.json', 'w') as fp:
        json.dump(final_dict, fp)

def find_per_game_avg():
    json_object = json.load(open("datasets/post80salldata.json"))
    per_game_dict = {}
    for person in json_object:
        person_stuff = json_object[person]
        per_game_data = person_stuff["all_per_game"]
        values = per_game_data[1:]
        data_change_lst = [7,8,9,11,12,14,15,18,19,21,22,23,24,25,26,27,28,29]
        for year_data in values:
            games = year_data[5]
            for column in data_change_lst:
                if year_data[column] != "N/A":
                    year_data[column] = float(year_data[column]) * float(games)
        career_per_game = [0] * len(per_game_data[1])
        go_through_stats = per_game_data[1:]
        divisors = [0] * len(per_game_data[1])
        for index in range(len(go_through_stats)):
            for index1 in range(len(go_through_stats[0])):
                if index1 > 4:
                    if (go_through_stats[index][index1]) != "N/A":
                        career_per_game[index1] += float(go_through_stats[index][index1])
                        divisors[index1] += float(go_through_stats[index][5])
        for index in range(len(career_per_game)):
            if index > 6:
                if divisors[index] != 0:
                    career_per_game[index] = career_per_game[index]/divisors[index]
        if career_per_game[9] != 0:
            career_per_game[10] = (career_per_game[8])/(career_per_game[9])
        if career_per_game[12] != 0:
            career_per_game[13] = (career_per_game[11])/(career_per_game[12])
        if career_per_game[15] != 0:
            career_per_game[16] = (career_per_game[14])/(career_per_game[15])
        if career_per_game[9] != 0:
            career_per_game[21] = (career_per_game[8] + 0.5 * career_per_game[11])/career_per_game[9]
        per_game_dict[person] = [per_game_data[0]] + [career_per_game]
    with open('datasets/reg_season_per_game.json', 'w') as fp:
        json.dump(per_game_dict, fp)

def find_optimal_k():
    json_object = json.load(open("reg_season_per_game.json"))
    json_object_height = json.load(open("data.json"))
    data = []
    for person in json_object:
        values = json_object[person]
        values_to_add = (values[1])[5:]
        first = (json_object_height[person])
        json_acceptable_string = first.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        curr_height = d['height']
        height_array = curr_height.split('-')
        final_height_inch = (int(height_array[0]) * 12) + int(height_array[1])
        values_to_add.append(final_height_inch)
        data.append(values_to_add)

    mms = MinMaxScaler()
    mms.fit(data)
    data_transformed = mms.transform(data)

    Sum_of_squared_distances = []
    K = range(1,15)
    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(data_transformed)
        Sum_of_squared_distances.append(km.inertia_)

    plt.plot(K, Sum_of_squared_distances, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Sum_of_squared_distances')
    plt.title('Elbow Method For Optimal k')
    plt.show()

def clustering_reg_season_avg():
    json_object = json.load(open("datasets/reg_season_per_game.json"))
    json_object_height = json.load(open("datasets/data.json"))
    data = []
    reverse_dict = {}
    for person in json_object:
        values = json_object[person]
        values_to_add = (values[1])[5:]
        gp = values_to_add[0]
        gs = values_to_add[1]
        start_rate = gs/gp
        values_to_add[0] = 1 - start_rate
        values_to_add[1] = start_rate
        first = (json_object_height[person])
        json_acceptable_string = first.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        curr_height = d['height']
        height_array = curr_height.split('-')
        final_height_inch = (int(height_array[0]) * 12) + int(height_array[1])
        values_to_add.append(final_height_inch)
        data.append(values_to_add)
        reverse_dict[repr(values_to_add)] = person
    km = KMeans(n_clusters=10, init='k-means++',
                max_iter=100, n_init=10, verbose=0, random_state=34)
    km = km.fit(data)
    final_dict = {}
    for index in range(len(km.labels_)):
        curr_category = km.labels_[index]
        curr_row = data[index]
        curr_person = reverse_dict[repr(curr_row)]
        (curr_row).append(curr_category)
        curr_row = [float(i) for i in curr_row]
        final_dict[curr_person] = curr_row
    with open('datasets/with_cat_reg_season_avg.json', 'w') as fp:
        json.dump(final_dict, fp)

def creating_final_cat_Dicts():
    json_object = json.load(open("datasets/with_cat_reg_season_avg.json"))
    keys = [0,1,2,3,4,5,6,7,8,9]
    cat_dict = {key: [] for key in keys}
    for person in json_object:
        curr_person_data = json_object[person]
        curr_category = (curr_person_data[-1])
        curr_lst = cat_dict[curr_category]
        curr_lst.append(person)
        cat_dict[curr_category] = curr_lst
    print(cat_dict[9])

    with open('datasets/regseasonavg_clusteringdict', 'w') as fp:
        json.dump(cat_dict, fp)

def find_advanced_avg():
    json_object = json.load(open("datasets/post80salldata.json"))
    per_game_dict = {}
    for person in json_object:
        person_stuff = json_object[person]
        per_game_data = person_stuff["all_advanced"]
        values = per_game_data[1:]
        data_change_lst = [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26]
        for year_data in values:
            games = year_data[5]
            for column in data_change_lst:
                if year_data[column] != "N/A":
                    year_data[column] = float(year_data[column]) * float(games)
        career_per_game = [0] * len(per_game_data[1])
        go_through_stats = per_game_data[1:]
        divisors = [0] * len(per_game_data[1])
        for index in range(len(go_through_stats)):
            for index1 in range(len(go_through_stats[0])):
                if index1 > 4:
                    if (go_through_stats[index][index1]) != "N/A":
                        career_per_game[index1] += float(go_through_stats[index][index1])
                        divisors[index1] += float(go_through_stats[index][5])
        for index in range(len(career_per_game)):
            if index > 6:
                if divisors[index] != 0:
                    career_per_game[index] = career_per_game[index]/divisors[index]
        per_game_dict[person] = [per_game_data[0]] + [career_per_game]
    with open('datasets/reg_season_advanced.json', 'w') as fp:
        json.dump(per_game_dict, fp)

def random_Crap():
    json_object = json.load(open("datasets/reg_season_advanced.json"))
    json_object_height = json.load(open("datasets/data.json"))
    data = []
    for person in json_object:
        values = json_object[person]
        values_to_add = (values[1])[5:]
        first = (json_object_height[person])
        json_acceptable_string = first.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        curr_height = d['height']
        height_array = curr_height.split('-')
        final_height_inch = (int(height_array[0]) * 12) + int(height_array[1])
        values_to_add.append(final_height_inch)
        data.append(values_to_add)

    mms = MinMaxScaler()
    mms.fit(data)
    data_transformed = mms.transform(data)

    Sum_of_squared_distances = []
    K = range(1,15)
    for k in K:
        km = KMeans(n_clusters=k)
        km = km.fit(data_transformed)
        Sum_of_squared_distances.append(km.inertia_)

    kneedle = KneeLocator(K, Sum_of_squared_distances, S=1.0, curve='convex', direction='decreasing')
    print(round(kneedle.knee, 3))

def final_run():
    json_object = json.load(open("datasets/reg_season_advanced.json"))
    json_object1 = json.load(open("datasets/reg_season_per_game.json"))
    json_object_height = json.load(open("datasets/data.json"))
    data = []
    reverse_dict = {}
    for person in json_object:
        values = json_object[person]
        values1 = json_object1[person]
        values_to_add = (values1[1])[5:]
        gp = values_to_add[0]
        gs = values_to_add[1]
        start_rate = gs/gp
        values_to_add[0] = 1 - start_rate
        values_to_add[1] = start_rate
        values_to_add1 = (values[1])[7:]
        final_values = values_to_add + values_to_add1
        first = (json_object_height[person])
        json_acceptable_string = first.replace("'", "\"")
        d = json.loads(json_acceptable_string)
        curr_height = d['height']
        height_array = curr_height.split('-')
        final_height_inch = (int(height_array[0]) * 12) + int(height_array[1])
        final_values.append(final_height_inch)
        data.append(final_values)
        reverse_dict[repr(final_values)] = person
    km = KMeans(n_clusters=16, init='k-means++',
                max_iter=100, n_init=10, verbose=0, random_state=34)
    km = km.fit(data)
    final_dict = {}
    for index in range(len(km.labels_)):
        curr_category = km.labels_[index]
        curr_row = data[index]
        curr_person = reverse_dict[repr(curr_row)]
        (curr_row).append(curr_category)
        curr_row = [float(i) for i in curr_row]
        final_dict[curr_person] = curr_row
    with open('datasets/with_cat_reg_season_advanced.json', 'w') as fp:
        json.dump(final_dict, fp)

    json_object = json.load(open("datasets/with_cat_reg_season_advanced.json"))
    keys = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
    cat_dict = {key: [] for key in keys}
    for person in json_object:
        curr_person_data = json_object[person]
        curr_category = (curr_person_data[-1])
        curr_lst = cat_dict[curr_category]
        curr_lst.append(person)
        cat_dict[curr_category] = curr_lst

    with open('datasets/final_data.json', 'w') as fp:
        json.dump(cat_dict, fp)

# json_object = json.load(open("datasets/reg_season_advanced.json"))
# print(json_object["LeBron James"])
