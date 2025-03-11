import streamlit as st

home = st.Page("etl.py", title="ETL")
page1 = st.Page("ai.py", title="AI")

pg = st.navigation([home, page1], position="sidebar")
pg.run()