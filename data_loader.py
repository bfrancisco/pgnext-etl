import pandas as pd
import re
import streamlit as st

def load_data(file):
    "takes a xlsx file and returns the shipments and pos dataframes"
    sheet_names = pd.ExcelFile(file).sheet_names
    shipments_sheet = next((s for s in sheet_names if re.search(r"Shipments", s, re.IGNORECASE)), None)
    pos_sheet = next((s for s in sheet_names if re.search(r"POS", s, re.IGNORECASE)), None)
    if not shipments_sheet or not pos_sheet:
        st.error("Required sheets not found")
        return None

    shipments_df = pd.read_excel(file, sheet_name=shipments_sheet)
    pos_df = pd.read_excel(file, sheet_name=pos_sheet)

    return shipments_df, pos_df

def load_supermarkets(file):
    "takes a txt file and returns a list of local supermarkets"
    with open(file, "r") as f:
        supermarkets = f.read().splitlines()
    return supermarkets


