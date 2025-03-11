import streamlit as st
import numpy as np
import pandas as pd
import time
import random


# prompt : (response, predefined_graph_index)
predefined_messages = {
    "Can you forecast the demand for this month?" : 
    (
    '''Sure! I’ve analyzed past sales, seasonal trends, and any patterns in your data. Here’s what I found:
    Downy: 15,200 units (increase from last month)
    Tide: 9,800 units (slight decrease)
    Would you like to provide additional data on factors like stock levels, supplier lead times, or upcoming promotions to refine the forecast?''',
    0),
}

predefined_graphs = [
    {"type": "bar", "data": pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), columns=['Ariel', 'Briel', 'Criel'])},
]

def response_generator(prompt):
    if prompt in predefined_messages:
        return {"text": predefined_messages[prompt][0], "chart": predefined_messages[prompt][1]}
    
    return {"text": "I'm sorry, I don't understand that question. Can you please rephrase it?", "chart": -1}

st.title("📊 TelaCast")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message.get("text", ""))
        if message.get("chart_type") and message.get("chart_data") is not None:
            if message["chart_type"] == "line":
                st.line_chart(message["chart_data"])
            elif message["chart_type"] == "bar":
                st.bar_chart(message["chart_data"])
            elif message["chart_type"] == "area":
                st.area_chart(message["chart_data"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "text": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get the next response
    response_info = response_generator(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.write(response_info["text"])
        
        # If this response includes a chart, generate and display it
        chart_data = None
        chart_type = None
        
        print(response_info)
        if response_info["chart"] != -1:
            chart = predefined_graphs[response_info["chart"]]
            chart_type = chart["type"]
            chart_data = chart["data"]
            
            if chart_type == "line":
                st.line_chart(chart_data)
            elif chart_type == "bar":
                st.bar_chart(chart_data)
            elif chart_type == "area":
                st.area_chart(chart_data)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "text": response_info["text"],
        "chart_type": chart_type,
        "chart_data": chart_data
    })