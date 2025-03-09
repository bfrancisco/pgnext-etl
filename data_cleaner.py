import re
from rapidfuzz import process, fuzz
import pandas as pd
import streamlit as st
import calendar

def clean_shipment(shipments_df, supermarkets, selected_products):
    # Drop empty columns
    shipments_df = shipments_df.dropna(axis=1, how='all')

    # Drop columns containing only zeroes
    shipments_df = shipments_df.loc[:, (shipments_df != 0).any(axis=0)] 

    # Rename the first column to "Products"
    shipments_df.columns.values[0] = "Product"

    # Rename all Robinsons variant to Robinsons
    row_num = 0
    for cell in shipments_df["Product"]:
        if "robinsons" in [c.lower() for c in cell.split()]:
            shipments_df.at[row_num, "Product"] = "Robinsons"
        row_num += 1

    # Get string and row number of valid local supermarkets
    valid_smarkets = []
    supermarkets_lower = [sm.lower() for sm in supermarkets]
    row_num = 0
    for cell in shipments_df["Product"]:
        match = levenshtein_match(cell, supermarkets_lower)
        if match:
            # if cell == "ROBINSONS DEP STORE":
            #     match = "Robinsons Department Store"
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

    shipments_df_melt = shipments_df.melt(id_vars=id_columns, var_name="Date", value_name="Shipment Amount (PHP)")
    shipments_df_melt[["Month", "Year"]] = shipments_df_melt["Date"].apply(extract_month_year)
    shipments_df_melt.drop(columns="Date", inplace=True)
    shipments_df_melt = shipments_df_melt[["Product", "Retailer", "Month", "Year", "Shipment Amount (PHP)"]]
    shipments_df = shipments_df_melt

    # Multiply shipment amount by 1,000,000
    shipments_df["Shipment Amount (PHP)"] = shipments_df["Shipment Amount (PHP)"] * 1000000

    # Drop rows with shipment amount equal to 0
    shipments_df.drop(shipments_df[shipments_df["Shipment Amount (PHP)"] == 0].index, inplace=True)
    
    # Change Month format
    shipments_df["Month"] = shipments_df["Month"].apply(lambda x: f"{list(calendar.month_abbr).index(x.capitalize()):02d}")

    return shipments_df

def clean_pos(pos_df, supermarkets, selected_products):
    pos_df.columns.values[0] = "Product"

    # Get string and row number of valid local supermarkets
    valid_smarkets = []
    supermarkets_lower = [sm.lower() for sm in supermarkets]
    row_num = 0
    for cell in pos_df["Product"]:
        match = levenshtein_match(cell, supermarkets_lower)
        if match:
            valid_smarkets.append((match.title(), row_num))
        row_num += 1

    # Create new column "Retailer" and input the corresponding supermarket for each product
    pos_df.insert(1, "Retailer", None)
    valid_i = 0 # index for valid_smarkets
    cur_retailer = ""
    to_drop_indices = []
    for pos_i, row in pos_df.iterrows():
        if pos_i == 0:
            continue
        elif valid_i < len(valid_smarkets) and pos_i == valid_smarkets[valid_i][1]:
            cur_retailer = valid_smarkets[valid_i][0]
            valid_i += 1
            to_drop_indices.append(pos_i)
        elif all(x == 0 or pd.isna(x) for x in row[1:]):
            # product category
            to_drop_indices.append(pos_i)
        elif cur_retailer == "":
            to_drop_indices.append(pos_i)
        else:
            pos_df.at[pos_i, "Retailer"] = cur_retailer
            
    for drop_i in to_drop_indices:
        pos_df.drop(drop_i, inplace=True)

    # Filter out unselected products
    pos_df.drop(pos_df[~pos_df["Product"].isin(selected_products)].index, inplace=True)

    # Change column headers
    col_headers = (pos_df.columns).tolist()
    prev_date = ""
    for col_i in range(2, len(col_headers)):
        if col_i%2==0:
            prev_date = col_headers[col_i]
            col_headers[col_i] = f"Sales Sum | {col_headers[col_i]}"
        else:
            col_headers[col_i] = f"Qty Sum | {prev_date}"
    pos_df.columns = col_headers

    # Combine into one row products with the same retailer.
    pos_df = pos_df.groupby(["Product", "Retailer"], as_index=False).sum()

    # Separate Month & Year to separate columns
    pos_df_melt = pos_df.melt(id_vars=["Product", "Retailer"], var_name="Metric", value_name="Value")

    pos_df_melt[["Metric Type", "Date"]] = pos_df_melt["Metric"].str.split(" \| ", expand=True)

    pos_df_melt["Year"] = pos_df_melt["Date"].str[:4]
    pos_df_melt["Month"] = pos_df_melt["Date"].str[5:]

    pos_df = pos_df_melt.pivot_table(index=["Product", "Retailer", "Year", "Month"], 
                                    columns="Metric Type", values="Value").reset_index()

    pos_df.columns.name = None
    pos_df.rename(columns={"Sales Sum": "Sales Sum", "Qty Sum": "Qty Sum"}, inplace=True)

    # Change Month format
    pos_df["Month"] = pos_df["Month"].apply(lambda x: f"{int(x):02d}")

    # Drop rows with Sales Sukm and Qty Sum equal to 0
    pos_df.drop(pos_df[(pos_df["Sales Sum"] == 0) & (pos_df["Qty Sum"] == 0)].index, inplace=True)

    # Reorder columns
    pos_df = pos_df[["Product", "Retailer", "Year", "Month", "Sales Sum", "Qty Sum"]]

    return pos_df

def combine_shipment_pos(shipments_df, pos_df):
    combined_df = pd.merge(shipments_df, pos_df, on=["Product", "Retailer", "Year", "Month"], how="outer")

    # Drop rows with NaN values
    combined_df.dropna(inplace=True)

    # Combine rows with the same Product, Retailer, Year, and Month
    combined_df = combined_df.groupby(["Product", "Retailer", "Year", "Month"], as_index=False).sum()

    combined_df.reset_index(drop=True, inplace=True)

    return combined_df

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
