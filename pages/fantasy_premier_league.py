import streamlit as st
import altair as alt
import pandas as pd
import os

st.set_page_config(layout="wide")

# Create inputs for filters
seasons = [
	{'display': '2025 - 2026', 'value': '2025_2026'},
	{'display': '2024 - 2025', 'value': '2024_2025'}
]

seasons_option_values = [season['value'] for season in seasons]

chart_coloring_dimensions = [
	{'display': 'Team', 'value': 'team_name'},
	{'display': 'Position', 'value': 'position'},
	{'display': 'Player Name', 'value': 'full_name'}
]

coloring_dimension_values = [dimension['value'] for dimension in chart_coloring_dimensions]

metrics = [
	{'display': 'Points', 'value': 'total_points'},
	{'display': 'Goals Scored', 'value': 'goals_scored'},
	{'display': 'Assists', 'value': 'assists'},
	{'display': 'Clean Sheets', 'value': 'clean_sheets'},
	{'display': 'Goals Conceded', 'value': 'goals_conceded'},
	{'display': 'Expected Goals', 'value': 'expected_goals'},
	{'display': 'Expected Assists', 'value': 'expected_assists'},
	{'display': 'Expected Goals Conceded', 'value': 'expected_goals_conceded'}
]

metric_option_values = [metric['value'] for metric in metrics]

def format_option_display(option_value):
	for season in seasons:
		if season['value'] == option_value:
			return season['display']
	for dimension in chart_coloring_dimensions:
		if dimension['value'] == option_value:
			return dimension['display']
	for metric in metrics:
		if metric['value'] == option_value:
			return metric['display']
	return option_value

## Layout filters and select data
first_row_cols = st.columns(3)
second_row_cols = st.columns(3)
with first_row_cols[0]:
	selected_season = st.selectbox(
		'Select season',
		options = seasons_option_values,
		index=0,
		format_func=format_option_display
	)
with first_row_cols[1]:
	selected_coloring_dimension = st.selectbox(
	'Select coloring dimension',
	options = coloring_dimension_values,
	index=None,
	format_func=format_option_display
)
with first_row_cols[2]:
	selected_metric = st.selectbox(
		'Select metric',
		options = metric_option_values,
		index = 0,
		format_func=format_option_display
	)

@st.cache_data
def load_data(selected_season):
	gameweek_data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', f'{selected_season}_filtered_gameweek_player_data.csv'))
	player_data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', f'{selected_season}_player_data_summary.csv'))
	player_data_cost_df = player_data[['player_id', 'now_cost']]
	gameweek_data = pd.merge(gameweek_data, player_data_cost_df, on='player_id', how='left')
	return gameweek_data, player_data

gameweek_data, player_data = load_data(selected_season)

with second_row_cols[0]:
	player_graph_option = st.multiselect(
		'Select Players',
		(player for player in sorted(gameweek_data['full_name'].unique()))
	)

	if player_graph_option:
		filtered_gameweek_data = gameweek_data[gameweek_data['full_name'].isin(player_graph_option)]
	else:
		filtered_gameweek_data = gameweek_data
with second_row_cols[1]:
	team_graph_option = st.multiselect(
		'Select Teams',
		(team for team in sorted(gameweek_data['team_name'].unique()))
	)

	if team_graph_option:
		filtered_gameweek_data = filtered_gameweek_data[filtered_gameweek_data['team_name'].isin(team_graph_option)]
with second_row_cols[2]:
	position_graph_option = st.multiselect(
		'Select Positions',
		(position for position in sorted(gameweek_data['position'].unique()))
	)

	if position_graph_option:
		filtered_gameweek_data = filtered_gameweek_data[filtered_gameweek_data['position'].isin(position_graph_option)]



## Create charts
viz_columns = st.columns((80, 10, 80))
metric_display_name = format_option_display(selected_metric)
with viz_columns[0]:
	st.subheader("Player Performance by Gameweek")
	if selected_coloring_dimension:
		avg_gameweek_points = filtered_gameweek_data.groupby(['gw_id', selected_coloring_dimension])[selected_metric].mean().round(2).reset_index()
		player_gameweek_data_chart = (
			alt.Chart(data=avg_gameweek_points)
			.mark_line(point=True)
			.encode(
				x=alt.X('gw_id', title='Gameweek'),
				y=alt.Y(selected_metric, title=metric_display_name),
				color=alt.Color(selected_coloring_dimension, title=selected_coloring_dimension.replace('_', ' ').title())
			)
		)
	elif selected_coloring_dimension is None:
		avg_gameweek_points = filtered_gameweek_data.groupby(['gw_id'])[selected_metric].mean().round(2).reset_index()
		player_gameweek_data_chart = (
			alt.Chart(data=avg_gameweek_points)
			.mark_line(point=True)
			.encode(x=alt.X('gw_id', title='Gameweek'), y=alt.Y(selected_metric, title=metric_display_name))
		)

	st.altair_chart(player_gameweek_data_chart)
with viz_columns[2]:
	st.subheader("Player Performance vs Cost")
	player_summary = filtered_gameweek_data.groupby(['full_name', 'position', 'team_name', 'now_cost'])[selected_metric].mean().round(2).reset_index()
	if selected_coloring_dimension:
		player_summary_scatter_chart = alt.Chart(player_summary).mark_point().encode(
			x=alt.X('now_cost', title='Now Cost'),
			y=alt.Y(selected_metric, title=metric_display_name),
			color=alt.Color(selected_coloring_dimension, title=selected_coloring_dimension.replace('_', ' ').title()),
			tooltip=[
						alt.Tooltip('full_name', title='Full Name'),
						alt.Tooltip(selected_metric, title=metric_display_name),
						alt.Tooltip('now_cost', title='Now Cost'),
						alt.Tooltip('position', title='Position'),
						alt.Tooltip('team_name', title='Team Name')
					]
		)
	elif selected_coloring_dimension is None:
		player_summary_scatter_chart = alt.Chart(player_summary).mark_point().encode(
			x=alt.X('now_cost', title='Cost'),
			y=alt.Y(selected_metric, title=metric_display_name),
			tooltip=[
						alt.Tooltip('full_name', title='Full Name'),
						alt.Tooltip(selected_metric, title=metric_display_name),
						alt.Tooltip('now_cost', title='Cost'),
						alt.Tooltip('position', title='Position'),
						alt.Tooltip('team_name', title='Team Name')
					]
		)
	
	st.altair_chart(player_summary_scatter_chart)
