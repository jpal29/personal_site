from pathlib import Path
from PIL import Image
import streamlit as st
import os


def read_markdown_file(markdown_file):
    return Path(markdown_file).read_text()

with st.sidebar:
	sidebar_markdown = read_markdown_file("sidebar.md")
	st.markdown(sidebar_markdown)


intro_markdown = read_markdown_file("index.md")

st.markdown(intro_markdown)
fpl_app_image = Image.open(os.path.join(os.path.dirname(__file__), "media", "fpl_screenshot.png"))
st.image(fpl_app_image)

risk_markdown = read_markdown_file("risk_outcomes.md")
st.markdown(risk_markdown)
risk_app_image = Image.open(os.path.join(os.path.dirname(__file__), "media", "risk_outcomes.png"))
st.image(risk_app_image)