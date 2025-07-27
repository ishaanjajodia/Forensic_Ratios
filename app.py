import streamlit as st
from utils import fetch_data_from_indianapi
from ratios import calculate_sloan_ratios

st.title("Forensic Stock Analyzer")

ticker = st.text_input("Enter Ticker Symbol (e.g., INFY):")

if ticker:
    try:
        data = fetch_data_from_indianapi(ticker)
        results = calculate_sloan_ratios(data)
        st.write("### Sloan Ratios")
        st.table(results)
    except Exception as e:
        st.error(str(e))
