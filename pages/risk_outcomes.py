import streamlit as st
import numpy as np
import plotly.graph_objects as go

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
    avg_att_troops_lost = np.mean(att_troops_lost_outcome)
    avg_def_troops_lost = np.mean(def_troops_lost_outcome)
    return att_troops_lost_outcome, avg_att_troops_lost, def_troops_lost_outcome, avg_def_troops_lost, perc_att_victory

def main():
    st.title("Risk Attacks Outcome")

    # Sidebar
    att_troop_num = st.sidebar.number_input("Number of attacking troops", min_value=1, max_value=100, value=1)
    def_troop_num = st.sidebar.number_input("Number of defending troops", min_value=1, max_value=100, value=1)

    if st.sidebar.button("Simulate"):
        st.text("Simulating Outcomes")
        att_troops_lost_outcome, avg_att_troops_lost, def_troops_lost_outcome, avg_def_troops_lost, perc_att_victory = sim_function(
            n=10000, attack_number=att_troop_num, def_number=def_troop_num
        )
        st.text(f"Probability of Attack Win: {perc_att_victory:.2%}")
        st.text(f"Expected Attacking Troops Lost: {avg_att_troops_lost:.2f}")
        st.text(f"Expected Defending Troops Lost: {avg_def_troops_lost:.2f}")

        st.subheader("Distribution of Attacking Troops Lost")
        att_troop_hist = go.Histogram(x=att_troops_lost_outcome, nbinsx=att_troop_num, showlegend=False)
        att_troop_layout = go.Layout(xaxis=dict(title="Attacking Troops Lost"), yaxis=dict(title="Count"), showlegend=False)
        st.plotly_chart(go.Figure(data=[att_troop_hist], layout=att_troop_layout), use_container_width=True)

        st.subheader("Distribution of Defending Troops Lost")
        def_troop_hist = go.Histogram(x=def_troops_lost_outcome, nbinsx=def_troop_num, showlegend=False)
        def_troop_layout = go.Layout(xaxis=dict(title="Defending Troops Lost"), yaxis=dict(title="Count"), showlegend=False)
        st.plotly_chart(go.Figure(data=[def_troop_hist], layout=def_troop_layout), use_container_width=True)


if __name__ == "__main__":
    main()