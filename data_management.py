import requests, json
import pandas as pd
import numpy as np
import os
from pprint import pprint

def join_for_player_name(gameweek_df, player_data_df, elements_to_rename):
	for element in elements_to_rename:
		gameweek_df = pd.merge(
			gameweek_df,
			player_data_df[['id', 'full_name']],
			left_on = element,
			right_on = 'id',
			how = 'left'
		)

		gameweek_df = gameweek_df.drop(['id_y'], axis=1)
		gameweek_df = gameweek_df.rename(columns={
			'full_name': element + '_full_name',
			'id_x': 'id'
			})

	return gameweek_df

def player_position_label(row):
    if row['element_type'] == 1:
        return 'Goalkeeper'
    elif row['element_type'] == 2:
        return 'Defender'
    elif row['element_type'] == 3:
    	return 'Midfielder'
    elif row['element_type'] == 4:
    	return 'Forward'

def get_player_meta_data(base_url):
	r = requests.get(base_url + 'bootstrap-static/').json()
	player_data = pd.DataFrame(r['elements'])
	player_data['full_name'] = player_data['first_name'] + ' ' + player_data['second_name']
	player_data['now_cost'] = player_data['now_cost']/10
	player_data['position'] = player_data.apply(player_position_label, axis=1)
	player_data.to_csv(os.path.join(os.path.dirname(__file__), "pages", "data", "player_data.csv"), index=False)
	return player_data

def get_meta_data(base_url, elements_to_rename):
	r = requests.get(base_url + 'bootstrap-static/').json()
	gameweek_data = pd.DataFrame(r['events'])
	player_data = get_player_meta_data(base_url)

	gameweek_data = gameweek_data[gameweek_data['average_entry_score'] > 0]

	gameweek_data = join_for_player_name(gameweek_data, player_data, elements_to_rename)
	gameweek_data.to_csv(os.path.join(os.path.dirname(__file__), "pages", "data", "gameweek_data.csv"), index=False)

# Get an individual gameweek's data.
def get_gameweek_data(gw_id):
	r = requests.get(base_url + 'event/' + str(gw_id) + '/live/').json()
	gameweek_data = pd.json_normalize(r['elements'])
	gameweek_data.drop(['explain', 'modified'], axis=1, inplace=True)
	gameweek_data.columns = gameweek_data.columns.str.replace('stats.', '')
	gameweek_data.rename(columns={'id': 'player_id'}, inplace=True)
	gameweek_data['gw_id'] = gw_id
	return gameweek_data

# Get each player's score by gameweek.
def get_all_gameweeks(base_url):
	r = requests.get(base_url + 'bootstrap-static/').json()
	gameweek_data = pd.DataFrame(r['events'])
	latest_gameweek = gameweek_data[gameweek_data['average_entry_score'] > 0]['id'].max()
	print(latest_gameweek)
	for gameweek in range(1, latest_gameweek + 1):
		if gameweek == 1:
			gameweek_df = get_gameweek_data(gameweek)
		else:
			gameweek_df = pd.concat([gameweek_df, get_gameweek_data(gameweek)])

	player_df = get_player_meta_data(base_url)

	gameweek_df = pd.merge(
			gameweek_df,
			player_df[['id', 'full_name']],
			left_on = 'player_id',
			right_on = 'id',
			how = 'left'
		)

	gameweek_df = gameweek_df.drop(['id'], axis=1)
	gameweek_df['player_cumulative_score'] = gameweek_df.groupby(['player_id'])['total_points'].cumsum()
	gameweek_df.to_csv(os.path.join(os.path.dirname(__file__), "pages", "data", "all_gameweek_player_data.csv"), index=False)


if __name__ == "__main__":
	base_url = 'https://fantasy.premierleague.com/api/'

	elements_to_rename = [
		'top_element',
		'most_captained',
		'most_vice_captained'
	]
	get_all_gameweeks(base_url=base_url)
	get_meta_data(base_url=base_url, elements_to_rename=elements_to_rename)