import streamlit as st
from utils import fetch_data_from_indianapi
from ratios import calculate_sloan_ratios, calculate_altman_z_scores, calculate_beneish_m_score

st.title("📊 Forensic Stock Analyzer")

ticker = st.text_input("Enter Ticker Symbol (e.g., INFY):")

if ticker:
    try:
        data = fetch_data_from_indianapi(ticker)

        st.header("Sloan Ratios")
        sloan = calculate_sloan_ratios(data)
        st.table(sloan)

        st.header("Altman Z-Score")
        altman = calculate_altman_z_scores(data)
        st.table(altman)

        st.header("Beneish M-Score")
        beneish = calculate_beneish_m_score(data)
        st.table(beneish)

    except Exception as e:
        st.error(str(e))
