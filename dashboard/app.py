import streamlit as st

# Konfigurasi dasar Halaman Utama
st.set_page_config(
    page_title="ABM Dashboard Simulasi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Landing page redirection (Home content)
st.title(" Dashboard Simulasi Agent-Based Modeling")
st.write("Selamat datang di perangkat lunak analisis simulasi pemilihan jurusan kuliah.")

st.info(" Silakan buka sidebar di sebelah kiri dan klik **1 Home** atau **2 Single Simulation** untuk mulai eksplorasi.")
