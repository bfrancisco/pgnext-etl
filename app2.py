import streamlit as st
import numpy as np
import pandas as pd
import time
import random

# Function to generate a random chart
def get_random_chart():
    chart_type = random.choice(["line", "bar", "area"])
    
    # Generate random data
    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c']
    )
    
    return {"type": chart_type, "data": chart_data}

# Sequential response generator with charts
def response_generator():
    # List of predetermined messages in sequence
    responses = [
        {"text": "Hello there! How can I assist you today?", "chart": False},
        {"text": "Here's a random chart for you:", "chart": True},
        {"text": "This is the third message in my sequence.", "chart": False},
        {"text": "Here's another visualization:", "chart": True},
        {"text": "After I run out of messages, I'll start over from the beginning.", "chart": False}
    ]
    
    # Get the current position in the sequence
    if "response_index" not in st.session_state:
        st.session_state.response_index = 0
    
    # Get the current response and increment the index
    response = responses[st.session_state.response_index]
    st.session_state.response_index = (st.session_state.response_index + 1) % len(responses)
    
    # Return the response information
    return response

st.title("Chat with Charts")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
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
    
    print(st.session_state)
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get the next response
    response_info = response_generator()
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.write(response_info["text"])
        
        # If this response includes a chart, generate and display it
        chart_data = None
        chart_type = None
        
        if response_info["chart"]:
            chart = get_random_chart()
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