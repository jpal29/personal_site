import streamlit as st
import altair as alt
import pandas as pd
import os


gameweek_data=pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', 'gameweek_data.csv'))
player_gameweek_data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', 'all_gameweek_player_data.csv'), index_col=False)
player_data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', 'player_data.csv'))

graph_col1, padding, graph_col2 = st.columns((80, 40, 80), gap="large")

with graph_col1:
	st.subheader("Player Performance by Gameweek")
	player_graph_option = st.selectbox(
		'Select Player',
		(player for player in sorted(player_gameweek_data['full_name'].unique()))
	)

	filtered_player_data = player_gameweek_data[player_gameweek_data['full_name'] == player_graph_option]

	player_gameweek_data_chart = (
			alt.Chart(
					data=filtered_player_data[['total_points', 'player_cumulative_score', 'gw_id']]
			)
			.encode(x=alt.X('gw_id', axis=alt.Axis(title='Gameweek')))
		)

	total_point_series = (
							player_gameweek_data_chart
							.mark_line(color='blue')
							.encode(y=alt.Y('total_points', axis=alt.Axis(title='Total Points')))
						)
	cumulative_point_series = (
								player_gameweek_data_chart
								.mark_line(color='red')
								.encode(y=alt.Y('player_cumulative_score', axis=alt.Axis(title='Cumulative Points')))
								)
	graph_tab_1, data_tab_1 = st.tabs(["Chart", "Data"])
	with graph_tab_1:
		st.altair_chart(alt.layer(cumulative_point_series, total_point_series).resolve_scale(y='independent'))
	
	with data_tab_1:
		st.write(filtered_player_data[['gw_id', 'total_points', 'player_cumulative_score']])


with graph_col2:
	st.subheader("Gameweek Performance")
	graph_metric_lookup = [{
		'Average Team Score': {'column': 'average_entry_score'},
		'Highest Team Score': {'column': 'highest_score'}
	}]

	graph_metric_option = st.selectbox(
			'Choose Gameweek Metric',
			(metric for metric in graph_metric_lookup[0])
		)

	gameweek_data_chart = (
			alt.Chart(
				data=gameweek_data
			)
			.mark_line()
			.encode(
				x=alt.X('id', axis=alt.Axis(title='Gameweek')),
				y=alt.Y(
					graph_metric_lookup[0][graph_metric_option]['column'],
					axis=alt.Axis(title=graph_metric_option))
			)
		)
	graph_tab_2, data_tab_2 = st.tabs(["Chart", "Data"])
	with graph_tab_2:
		st.altair_chart(gameweek_data_chart)

	with data_tab_2:
		st.write(gameweek_data[['id', graph_metric_lookup[0][graph_metric_option]['column']]])

st.write("Gameweek Stats")
st.dataframe(data=gameweek_data[['id',
					'average_entry_score',
					'highest_score',
					'top_element_full_name',
					'most_captained_full_name',
					'most_vice_captained_full_name']]
					.rename(columns={
						'id': 'Gameweek',
						'average_entry_score': 'Average Score',
						'highest_score': 'Highest Score',
						'top_element_full_name': 'Highest Scoring Player',
						'most_captained_full_name': 'Most Captained',
						'most_vice_captained_full_name': 'Most Vice Captained'
						}))

players = player_data['full_name']
pick_players = st.multiselect('Select Player', players)

player_stats_filtered = player_data[player_data['full_name'].isin(pick_players)]
st.write("Player Stats")
if len(pick_players) > 0:
	st.dataframe(data=player_stats_filtered[['full_name',
						'position',
						'total_points',
						'points_per_game',
						'now_cost',
						'goals_scored',
						'expected_goals_per_90',
						'assists',
						'clean_sheets']]
						.rename(columns={
							'full_name': 'Name',
							'position': 'Position',
							'total_points': 'Total Points',
							'points_per_game': 'Points per Game',
							'now_cost': 'Cost',
							'goals_scored': 'Goals Scored',
							'expected_goals_per_90': 'Expected Goals per 90',
							'assists': 'Assists',
							'clean_sheets': 'Clean Sheets'
							}))
else:
	st.dataframe(data=player_data[['full_name',
						'position',
						'total_points',
						'points_per_game',
						'now_cost',
						'goals_scored',
						'expected_goals_per_90',
						'assists',
						'clean_sheets']]
						.rename(columns={
							'full_name': 'Name',
							'position': 'Position',
							'total_points': 'Total Points',
							'points_per_game': 'Points per Game',
							'now_cost': 'Cost',
							'goals_scored': 'Goals Scored',
							'expected_goals_per_90': 'Expected Goals per 90',
							'assists': 'Assists',
							'clean_sheets': 'Clean Sheets'
							}))




