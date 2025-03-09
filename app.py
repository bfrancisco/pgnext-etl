import streamlit as st
from data_loader import load_data, load_supermarkets, load_png_products
from data_cleaner import clean_data

def main():
    st.title("Team OlayFans ETL App")
    
    png_products = load_png_products("png_products.txt")
    selected_products = st.multiselect("Select products to filter", png_products, default=["Ariel", "Downy", "Tide"])
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])
    
    if uploaded_file is not None:
        supermarkets = load_supermarkets("local_supermarkets.txt")
        shipments_df, pos_df = load_data(uploaded_file)
        
        if not shipments_df.empty and not pos_df.empty:
            st.write("Original Data")
            st.write(shipments_df)
            
            cleaned_df = clean_data(shipments_df, pos_df, supermarkets, selected_products)
            
            st.write("Cleaned Data")
            st.write(cleaned_df)
            
            cleaned_file = st.download_button(
                label="Download Cleaned Data",
                data=cleaned_df.to_csv(index=False).encode('utf-8'),
                file_name='cleaned_data.csv',
                mime='text/csv'
            )

if __name__ == "__main__":
    main()