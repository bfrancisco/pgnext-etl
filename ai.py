import streamlit as st
import numpy as np
import pandas as pd
import time
import random


# prompt : [response per line]
predefined_messages = {
    "Predict demand for Downy in Q1 2025 using past 6 months' shipments." : 
    [
        "Predicted demand for Downy in Q1 2025 shows a gradual increase from 3,200 to 3,800 units. The forecast was generated using the SARIMA model, which analyzed the past 6 months of shipment data (July to December 2024). The model accounts for seasonal patterns, trends, and recent fluctuations to ensure accurate forecasting.",
        "Additionally, the prediction was cross-validated using actual sales data from Q3 and Q4 2024, achieving an accuracy rate of 92%. This accuracy metric was calculated by comparing predicted values with actual sales in previous quarters. The model also considered seasonal impacts and promotional events recorded in the Season_Holiday column.",
        "Given the upward trend observed, it is advisable to maintain higher stock levels for Downy in Q1 2025 to meet the increasing demand, especially during peak periods or promotional events."
    ],
    "Compare last quarter’s demand forecast with actual sales. Where were the biggest discrepancies, and what might have caused them? With the data given, create a PowerBi dashboard as well." :
    [
        "I compared last quarter’s demand forecast with actual sales and used Mean Absolute Percentage Error (MAPE) to measure accuracy.",
        "## Step 1: Forecast vs. Actual Comparison",
        "MAPE: 5.1% → Acceptable, but Month 3 had the largest deviation.",
        "## Step 2: Root Cause Analysis",
        "I analyzed potential causes using correlation analysis between forecast errors and external factors:",
        "**Month 1 (Over-prediction): Sales were higher due to an unanticipated surge in demand from a successful promotion.**",
        "**Month 2 (Accurate): No major discrepancies.**",
        "**Month 3 (Under-prediction):**",
        " - Shipments arrived late → less stock available for sale.",
        " - Consumer demand was weaker than expected → possible seasonal shift or competitor pricing effects.",
        "## Step 3: Recommendations",
        "   - Improve promotional impact modeling to reduce Month 1 forecast error.",
        "   - Incorporate real-time shipment tracking into forecasting models to adjust for stock availability.",
        "   - Refine seasonality adjustments to capture shifts in demand patterns.",
    ],
}

# for 2nd predetermined mssg
table_data = {
    'Month': ['Month 1', 'Month 2', 'Month 3'],
    'Forecasted Demand': [12500, 11200, 10800],
    'Actual Sales': [13100, 10900, 9950],
    'Error (%)': ['+4.8%', '-2.7%', '-7.8% 🚨']
}

table_df = pd.DataFrame(table_data)

def response_generator(prompt):
    if prompt in predefined_messages:
        return {
            "texts": predefined_messages[prompt],
            "image": ("img/response1img.png" if prompt.split()[0] == "Predict" else "img/response2img.png")
        }
    
    return {"texts": ["I'm sorry, I don't understand that question. Can you please rephrase it?"]}

def stream_text(texts):
    for word in text.split():
        yield word + " "
        time.sleep(0.05)
    st.write("")

st.title("📊 TelaCast+")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for text in message.get("texts", []):
            st.markdown(text)
        if "image" in message and message["image"] != None:
            st.image(message["image"])
        # st.markdown(message.get("text", ""))

# Accept user input
if prompt := st.chat_input("What can I forecast for you today?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "texts": [prompt]})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # loading
    time.sleep(2)
    
    # Get the next response
    response_info = response_generator(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        for text in response_info["texts"]:
            placeholder = st.empty()
            for i in range(len(text)):
                placeholder.markdown(text[:i+1])
                time.sleep(0.02)
            if (text == "## Step 1: Forecast vs. Actual Comparison"):
                st.write(table_df)

        if "image" in response_info and response_info["image"] != None:
            st.image(response_info["image"])
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "texts": response_info["texts"],
        "image": response_info.get("image", None)
    })

