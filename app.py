import streamlit as st
from utils import fetch_data_from_indianapi
from ratios import calculate_sloan_ratios, calculate_altman_z_scores

st.title("🕵️‍♂️ Forensic Stock Analyzer")

ticker = st.text_input("Enter Ticker Symbol (e.g., INFY):")

if ticker:
    try:
        data = fetch_data_from_indianapi(ticker)

        # Sloan Ratios
        sloan = calculate_sloan_ratios(data)
        st.subheader("📘 Sloan Ratios")
        st.table(sloan)

        # Altman Z-Score
        altman = calculate_altman_z_scores(data)
        st.subheader("📗 Altman Z-Score (Bankruptcy Risk)")
        st.table(altman)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
