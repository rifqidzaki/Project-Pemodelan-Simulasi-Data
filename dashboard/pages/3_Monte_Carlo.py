import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import math
import sys
import os

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import MajorSelectionModel
from utils import format_metric

st.set_page_config(page_title="Monte Carlo", layout="wide")
st.title(" Analisis Monte Carlo")
st.write("Jalankan simulasi ribuan kali untuk memastikan reliabilitas statistik model yang robust.")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header(" Konfigurasi Monte Carlo")
n_iterations = st.sidebar.selectbox("Jumlah Iterasi", [100, 500, 1000, 5000], index=0)
n_steps = st.sidebar.number_input("Time Step per Iterasi", min_value=10, max_value=100, value=50)

st.sidebar.markdown("---")
st.sidebar.subheader("Parameter Lingkungan Tetap")
stressor = st.sidebar.slider("Stressor", 0.0, 1.0, 0.5)
cbt = st.sidebar.slider("CBT", 0.0, 1.0, 0.5)
informasi = st.sidebar.slider("Informasi", 0.0, 1.0, 0.5)
prospek = st.sidebar.slider("Prospek", 0.0, 1.0, 0.6)

def run_monte_carlo(iters, steps, s, c, i, p):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for it in range(iters):
        # Jalankan satu model hingga time steps tertentu
        m = MajorSelectionModel(
            n_agents=30, width=10, height=10,
            information=i, prospect=p, stressor=s, cbt=c, seed=it
        )
        m.run(steps)
        df = m.datacollector.get_model_vars_dataframe()
        dist = m.get_state_distribution()
        
        results.append({
            'iteration': it,
            'avg_anxiety': df['Avg_C'].iloc[-1],
            'avg_score': df['Avg_Score'].iloc[-1],
            'pct_yakin': (dist['Yakin'] / 30) * 100,
            'pct_salah': (dist['Salah'] / 30) * 100
        })
        
        # Update UI progress bar secara efisien
        if it % max(1, (iters // 20)) == 0:
            progress_bar.progress(it / iters)
            status_text.text(f" Sedang menjalankan iterasi {it}/{iters}...")
            
    progress_bar.progress(1.0)
    status_text.text(" Simulasi Monte Carlo Selesai!")
    return pd.DataFrame(results)

if st.sidebar.button(" Mulai Monte Carlo", type="primary", use_container_width=True):
    with st.spinner(f"Memproses {n_iterations} iterasi... Sistem sedang bekerja keras. "):
        df_mc = run_monte_carlo(n_iterations, n_steps, stressor, cbt, informasi, prospek)
        st.session_state.df_mc = df_mc

# --- OUTPUT HASIL MONTE CARLO ---
if 'df_mc' in st.session_state:
    df = st.session_state.df_mc
    
    st.markdown("---")
    st.subheader(" Analisis Deskriptif & Confidence Interval")
    
    # Perhitungan Statistik
    mean_anxiety = df['avg_anxiety'].mean()
    std_anxiety = df['avg_anxiety'].std()
    ci95_anx = 1.96 * std_anxiety / math.sqrt(n_iterations)
    
    mean_score = df['avg_score'].mean()
    std_score = df['avg_score'].std()
    ci95_score = 1.96 * std_score / math.sqrt(n_iterations)
    
    # Tampilkan Metrics Card Berjejer
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mean Anxiety", format_metric(mean_anxiety))
    c2.metric("Median Anxiety", format_metric(df['avg_anxiety'].median()))
    c3.metric("Variance Anxiety", format_metric(df['avg_anxiety'].var()))
    c4.metric("95% CI Anxiety", f"± {ci95_anx:.4f}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Mean Score", format_metric(mean_score))
    c6.metric("Median Score", format_metric(df['avg_score'].median()))
    c7.metric("Variance Score", format_metric(df['avg_score'].var()))
    c8.metric("95% CI Score", f"± {ci95_score:.4f}")

    st.markdown("---")
    
    # Distribusi Histogram
    st.subheader(" Distribusi Hasil")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Histogram Anxiety dengan Marginal Boxplot di atasnya
        fig_hist_anx = px.histogram(df, x="avg_anxiety", marginal="box", nbins=50,
                                    title="Distribusi Anxiety (Kerapatan Kepadatan)", 
                                    color_discrete_sequence=['#E74C3C'])
        fig_hist_anx.update_layout(template="plotly_dark")
        st.plotly_chart(fig_hist_anx, use_container_width=True)
        
    with col_b:
        fig_hist_score = px.histogram(df, x="avg_score", marginal="box", nbins=50,
                                      title="Distribusi Score Kesesuaian", 
                                      color_discrete_sequence=['#3498DB'])
        fig_hist_score.update_layout(template="plotly_dark")
        st.plotly_chart(fig_hist_score, use_container_width=True)
        
    # Boxplot Perbandingan
    st.subheader(" Boxplot Analysis")
    fig_box = px.box(df, y=["pct_yakin", "pct_salah"], title="Perbandingan Sebaran Persentase Yakin vs Salah Jurusan",
                     color_discrete_sequence=['#27AE60', '#E74C3C'])
    fig_box.update_layout(template="plotly_dark", yaxis_title="Persentase (%)")
    st.plotly_chart(fig_box, use_container_width=True)
    
    # Eksport ke CSV
    st.markdown("---")
    st.subheader(" Export Data Mentah")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=" Download Data Monte Carlo (.csv)",
        data=csv,
        file_name='monte_carlo_results_dashboard.csv',
        mime='text/csv',
    )
else:
    st.info(" Silakan konfigurasikan parameter Monte Carlo di Sidebar lalu klik tombol **'Mulai Monte Carlo'**.")
