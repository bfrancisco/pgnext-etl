import streamlit as st

home = st.Page("app.py", title="ETL")
page1 = st.Page("app2.py", title="AI")

pg = st.navigation([home, page1], position="sidebar")
pg.run()