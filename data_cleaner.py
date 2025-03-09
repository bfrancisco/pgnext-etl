import re
from rapidfuzz import process, fuzz
import streamlit as st 

def clean_data(shipments_df, pos_df, supermarkets, selected_products):
    # Drop empty columns
    shipments_df = shipments_df.dropna(axis=1, how='all')

    # Drop columns containing all zero
    shipments_df = shipments_df.loc[:, (shipments_df != 0).any(axis=0)] 

    # Rename the first column to "Products"
    shipments_df.columns.values[0] = "Products"

    # Get string and row number of valid local supermarkets
    valid_smarkets = []
    supermarkets_lower = [sm.lower() for sm in supermarkets]
    row_num = 0
    for cell in shipments_df["Products"]:
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
    shipments_df.drop(shipments_df[~shipments_df["Products"].isin(selected_products)].index, inplace=True)

    return shipments_df

def levenshtein_match(product_or_smarket, supermarkets):
    match, score, _ = process.extractOne(product_or_smarket.lower(), supermarkets, scorer=fuzz.ratio)
    if score < 75:
        return None
    return match