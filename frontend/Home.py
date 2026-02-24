from pathlib import Path
import streamlit as st
from frontend.ui.ui_framework import page_setup

page_setup(title="Reptile Central", icon="🦎")

st.title("Welcome to the Reptile Central Database Manager!")
st.write(
    "Use this website to view and manage our animals, products, customers and orders. "
)
st.image(str(Path(__file__).resolve().parent / "assets" / "leopard_gecko.jpg"), width="content")
