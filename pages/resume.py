from streamlit_pdf_viewer import pdf_viewer
import streamlit as st

with open("media/joshua_lee_resume.pdf", "rb") as pdf_file:
    PDFbyte = pdf_file.read()

st.download_button(
	label="Download Resume",
	data=PDFbyte,
	file_name="joshua_lee_resume.pdf"
)

pdf_viewer('media/joshua_lee_resume.pdf')