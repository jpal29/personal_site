from pathlib import Path
from PIL import Image
import streamlit as st
from streamlit_card import card
import os


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

st.header("Featured Work")
st.write('----')

with st.sidebar:
	sidebar_markdown = read_markdown_file("sidebar.md")
	st.markdown(sidebar_markdown)

st.set_page_config(layout="wide")
risk_markdown = read_markdown_file("risk_outcomes.md")
risk_app_image = Image.open(os.path.join(os.path.dirname(__file__), "media", "risk_outcomes.png"))
fpl_markdown = read_markdown_file("fantasy_premier_league.md")
fpl_app_image = Image.open(os.path.join(os.path.dirname(__file__), "media", "fpl_screenshot.png"))


with st.container(border=True):
	st.markdown(risk_markdown)

with st.container(border=True):
	st.markdown(fpl_markdown)