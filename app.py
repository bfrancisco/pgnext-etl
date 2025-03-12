import streamlit as st

etl_page = st.Page("etl.py", title="Data Cleaning")
ai_page = st.Page("ai.py", title="TelaCast+")

pg = st.navigation([etl_page, ai_page], position="sidebar")
pg.run()