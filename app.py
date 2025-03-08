import streamlit as st
from data_loader import load_data
from data_cleaner import clean_data

def main():
    st.title("Team OlayFans ETL App")
    
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])
    
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        
        if data is not None:
            st.write("Original Data")
            st.write(data)
            
            cleaned_data = clean_data(data)
            
            st.write("Cleaned Data")
            st.write(cleaned_data)
            
            cleaned_file = st.download_button(
                label="Download Cleaned Data",
                data=cleaned_data.to_csv(index=False).encode('utf-8'),
                file_name='cleaned_data.csv',
                mime='text/csv'
            )

if __name__ == "__main__":
    main()