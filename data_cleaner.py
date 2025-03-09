import re
from rapidfuzz import process, fuzz
import pandas as pd
import streamlit as st

def clean_data(shipments_df, pos_df, supermarkets, selected_products):
    # Drop empty columns
    shipments_df = shipments_df.dropna(axis=1, how='all')

    # Drop columns containing only zeroes
    shipments_df = shipments_df.loc[:, (shipments_df != 0).any(axis=0)] 

    # Rename the first column to "Products"
    shipments_df.columns.values[0] = "Product"

    # Get string and row number of valid local supermarkets
    valid_smarkets = []
    supermarkets_lower = [sm.lower() for sm in supermarkets]
    row_num = 0
    for cell in shipments_df["Product"]:
        match = levenshtein_match(cell, supermarkets_lower)
        if match:
            if cell == "ROBINSONS DEP STORE":
                match = "Robinsons Department Store"
            valid_smarkets.append((match.title(), row_num))
        row_num += 1
    
    # Create new column "Retailer" and input the corresponding supermarket for each product
    shipments_df.insert(1, "Retailer", None)
    valid_i = 0 # index for valid_smarkets
    cur_retailer = ""
    for shipments_i, row in shipments_df.iterrows():
        if valid_i < len(valid_smarkets) and shipments_i == valid_smarkets[valid_i][1]:
            cur_retailer = valid_smarkets[valid_i][0]
            valid_i += 1
        else:
            shipments_df.at[shipments_i, "Retailer"] = cur_retailer 
    
    for _, drop_i in valid_smarkets:
        shipments_df.drop(drop_i, inplace=True)

    # Filter out unselected products
    shipments_df.drop(shipments_df[~shipments_df["Product"].isin(selected_products)].index, inplace=True)

    # Convert all undefined cells to 0
    shipments_df = shipments_df.fillna(0)
    
    # Separate Month & Year to separate columns 
    date_columns = [col for col in shipments_df.columns if is_date_header(col)]
    id_columns = [col for col in shipments_df.columns if col not in date_columns]

    shipments_df_melt = shipments_df.melt(id_vars=id_columns, var_name="Date", value_name="Shipment Amount (MM PHP)")
    shipments_df_melt[["Month", "Year"]] = shipments_df_melt["Date"].apply(extract_month_year)
    shipments_df_melt.drop(columns="Date", inplace=True)
    shipments_df_melt = shipments_df_melt[["Product", "Retailer", "Month", "Year", "Shipment Amount (MM PHP)"]]
    shipments_df = shipments_df_melt
    return shipments_df

def levenshtein_match(product_or_smarket, supermarkets):
    match, score, _ = process.extractOne(product_or_smarket.lower(), supermarkets, scorer=fuzz.ratio)
    if score < 75:
        return None
    return match

def is_date_header(header):
    c_header = header.upper().strip()
    return re.match(r"([A-Z]{3})(\d{4})", c_header)

def extract_month_year(date_str):
    c_date_str = date_str.upper().strip()
    match = re.match(r"([A-Z]{3})(\d{4})", c_date_str)
    if match:
        month, year = match.groups()
        return pd.Series([month, year], index=["Month", "Year"])
    return pd.Series([None, None])
