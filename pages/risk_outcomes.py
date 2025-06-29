import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
from pathlib import Path

def one_shake_function(att_troop_per_shake, def_troop_per_shake):
    dice = np.arange(1, 7)
    att_shake = np.sort(np.random.choice(dice, size=att_troop_per_shake, replace=True))[::-1]
    def_shake = np.sort(np.random.choice(dice, size=def_troop_per_shake, replace=True))[::-1]
    dice_in_play = min(att_troop_per_shake, def_troop_per_shake)
    att_shake_in_play = att_shake[:dice_in_play]
    def_shake_in_play = def_shake[:dice_in_play]
    result = att_shake_in_play > def_shake_in_play
    att_troops_lost = np.sum(result == False)
    def_troops_lost = np.sum(result == True)
    return att_troops_lost, def_troops_lost

def attack_function(attack_no, def_no):
    att_troops_left = attack_no
    def_troops_left = def_no
    while att_troops_left > 0 and def_troops_left > 0:
        att_troops_available = min(3, att_troops_left)
        def_troops_available = min(2, def_troops_left)
        troops_lost = one_shake_function(att_troops_available, def_troops_available)
        att_troops_left -= troops_lost[0]
        def_troops_left -= troops_lost[1]
    return att_troops_left, def_troops_left

def sim_function(n, attack_number, def_number):
    win_outcomes = []
    att_troops_lost_outcome = []
    def_troops_lost_outcome = []
    for _ in range(n):
        result = attack_function(attack_number, def_number)
        att_troops_left = result[0]
        def_troops_left = result[1]
        att_troops_lost = attack_number - att_troops_left
        def_troops_lost = def_number - def_troops_left
        att_victory = att_troops_left > def_troops_left
        win_outcomes.append(att_victory)
        att_troops_lost_outcome.append(att_troops_lost)
        def_troops_lost_outcome.append(def_troops_lost)
    perc_att_victory = sum(win_outcomes) / n
    attack_df = pd.DataFrame(att_troops_lost_outcome, columns=["Att. Troops Lost"])
    attack_df = attack_df.groupby('Att. Troops Lost').size().reset_index()
    attack_df.rename(columns={0: 'Att. Troops Lost Frequency'}, inplace=True)
    attack_df['Att. Troops - Percent of Total'] = (attack_df['Att. Troops Lost Frequency'] / attack_df['Att. Troops Lost Frequency'].sum())

    defend_df = pd.DataFrame(def_troops_lost_outcome, columns=['Def. Troops Lost'])
    defend_df = defend_df.groupby('Def. Troops Lost').size().reset_index()
    defend_df.rename(columns={0: 'Def. Troops Lost Frequency'}, inplace=True)
    defend_df['Def. Troops - Percent of Total'] = (defend_df['Def. Troops Lost Frequency']/ defend_df['Def. Troops Lost Frequency'].sum())

    results_df = pd.merge(attack_df, defend_df, left_index=True, right_index=True, how='outer')

    return perc_att_victory, results_df

def main():
    st.set_page_config(layout="wide")

    st.title("Risk Attacks Outcome")

    risk_markdown = Path("risk_outcomes.md").read_text()
    st.markdown(risk_markdown)

    # Sidebar
    att_troop_num = st.sidebar.number_input("Number of attacking troops", min_value=1, max_value=100, value=10)
    def_troop_num = st.sidebar.number_input("Number of defending troops", min_value=1, max_value=100, value=5)
    simulations = st.sidebar.number_input("Simulations", min_value = 1, max_value=100000, value=10000)

    perc_att_victory, results_df = sim_function(n=simulations, attack_number=att_troop_num, def_number=def_troop_num)

    if st.sidebar.button("Simulate"):
        perc_att_victory, results_df = sim_function(n=simulations, attack_number=att_troop_num, def_number=def_troop_num)

    avg_att_troops_lost = (results_df['Att. Troops - Percent of Total'] * results_df['Att. Troops Lost']).sum()
    avg_def_troops_lost = (results_df['Def. Troops - Percent of Total'] * results_df['Def. Troops Lost']).sum()

    result_output_df = pd.DataFrame.from_dict({'Expected Attacking Troops Lost': [f'{avg_att_troops_lost:.2f}'],
                                                'Expected Defending Troops Lost': [f'{avg_def_troops_lost:.2f}'],
                                                'Probability of Attack Win': [f'{perc_att_victory:.1%}']})

    result_output_df.index = ['Values']*len(result_output_df)
    result_output_df = result_output_df.T


    fig = go.Figure(go.Scatter(x=results_df['Att. Troops Lost'],
                                y=results_df['Att. Troops - Percent of Total'],
                                mode='lines+markers',
                                name = 'Attacking Troops'))

    fig.add_trace(go.Scatter(x=results_df['Def. Troops Lost'],
                                y=results_df['Def. Troops - Percent of Total'],
                                mode='lines+markers',
                                name='Defending Troops'))

    fig.add_trace(go.Scatter(x=[avg_att_troops_lost]*11,
                                y=np.arange(0, 1.1, .1),
                                mode='lines',
                                line=dict(dash='dash', color='black'),
                                name='Expected Attacking Troops Lost'))

    fig.add_trace(go.Scatter(x=[avg_def_troops_lost]*11,
                                y=np.arange(0, 1.1, .1),
                                mode='lines',
                                line=dict(dash='dash', color='gray'),
                                name='Expected Defending Troops Lost'))
    fig.update_yaxes(range=[0, 1.05])
    fig.update_layout(xaxis_title='Troops Lost',
                        yaxis_title='Likelihood of loss',
                        showlegend=True,
                        yaxis=dict(tickformat='.2%'))
    chart_column, table_column = st.columns([.7, .3], vertical_alignment="center")

    with chart_column:
        st.plotly_chart(fig, use_container_width=True)
    with table_column:
        st.table(result_output_df)


if __name__ == "__main__":
    main()