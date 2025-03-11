import streamlit as st
from data_loader import load_data, load_supermarkets, load_png_products
from data_cleaner import clean_shipment, clean_pos, combine_shipment_pos

def main():
    st.set_page_config(page_title="OlayFans App", page_icon="🧹", layout="wide")
    st.title("🧹 OlayFans Data Cleaning App")
    
    png_products = load_png_products("png_products.txt")
    selected_products = st.multiselect("Select products to filter", png_products, default=["Ariel", "Downy", "Tide"])
    uploaded_file = st.file_uploader("Choose a file", type=["xlsx"])
    
    if uploaded_file is not None:
        supermarkets = load_supermarkets("local_supermarkets.txt")
        shipments_df, pos_df = load_data(uploaded_file)
        
        if not shipments_df.empty and not pos_df.empty:
            cleaned_shipments_df = clean_shipment(shipments_df, supermarkets, selected_products)
            cleaned_pos_df = clean_pos(pos_df, supermarkets, selected_products)
            
            # st.write(cleaned_shipments_df)
            # st.write(cleaned_pos_df)
            
            combined_df = combine_shipment_pos(cleaned_shipments_df, cleaned_pos_df)

            st.header("Master Dataset Preview")
            st.write(combined_df)
            cleaned_file = st.download_button(
                label="Download Master Dataset",
                data=combined_df.to_csv(index=False).encode('utf-8'),
                file_name='cleaned_data.csv',
                mime='text/csv',
                use_container_width=True
            )

main()