import streamlit as st
from utils import fetch_data_from_indianapi
from ratios import calculate_sloan_ratios, calculate_altman_z_scores, calculate_f_scores

st.title("🔍 Forensic Stock Analyzer")

ticker = st.text_input("Enter Ticker Symbol (e.g., INFY, TCS, DISHMAN):")

if ticker:
    try:
        data = fetch_data_from_indianapi(ticker)

        st.subheader("📘 Sloan Ratios")
        sloan = calculate_sloan_ratios(data)
        st.table(sloan)

        st.subheader("📊 Altman Z-Scores")
        altman = calculate_altman_z_scores(data)
        st.table(altman)

        st.subheader("📈 Piotroski F-Scores")
        fscore = calculate_f_scores(data)
        st.table(fscore)

    except Exception as e:
        st.error(f"Error: {str(e)}")
