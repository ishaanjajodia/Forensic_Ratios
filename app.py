import streamlit as st
from utils import fetch_data_from_indianapi
from ratios import (
    calculate_sloan_ratios,
    calculate_altman_z_scores,
    calculate_beneish_m_score,
    calculate_piotroski_f_score
)

st.title("📊 Forensic Stock Analyzer")

ticker = st.text_input("Enter Ticker Symbol (e.g., INFY):").upper()

if ticker:
    try:
        with st.spinner("Fetching and analyzing data..."):
            data = fetch_data_from_indianapi(ticker)

            st.header("Sloan Ratios")
            sloan = calculate_sloan_ratios(data)
            st.subheader("📘 Sloan Ratios")
            st.table(sloan)

            st.header("Altman Z-Score")
            altman = calculate_altman_z_scores(data)
            st.subheader("📗 Altman Z-Score (Bankruptcy Risk)")
            st.table(altman)

            st.header("Beneish M-Score")
            beneish = calculate_beneish_m_score(data)
            st.subheader("📙 Beneish M-Score (Earnings Manipulation Risk)")
            st.table(beneish)

            
            fscore_results = calculate_piotroski_f_score(data)

            st.subheader("📘 Piotroski F-Score")
            st.table([
            {
              'Year': res['Year'],
              'F-Score': res['F-Score'],
              'Criteria': ', '.join(['✔️' if c else '❌' for c in res['Criteria']])
               } for res in fscore_results
                      ])


    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.caption("📉 These forensic ratios are for educational purposes only and not investment advice.")
