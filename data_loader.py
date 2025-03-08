import pandas as pd
import streamlit as st

def load_data(file):
    data = None
    if file.name.endswith('.csv'):
        data = pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        data = pd.read_excel(file)
    else:
        st.error("Unsupported file format")
    return data