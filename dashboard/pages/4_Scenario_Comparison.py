import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import math

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import MajorSelectionModel

st.set_page_config(page_title="Scenario Comparison", layout="wide")
st.title(" Scenario Comparison")
st.write("Bandingkan metrik kinerja dari 4 skenario eksperimen secara head-to-head untuk evaluasi mendalam.")

# Definisi Skenario
SCENARIOS = {
    'Sk 1: Tanpa Intervensi': {'stressor': 0.8, 'cbt': 0.0, 'information': 0.2, 'prospect': 0.5},
    'Sk 2: Tekanan Sosial Tinggi': {'stressor': 0.6, 'cbt': 0.2, 'information': 0.2, 'prospect': 0.5},
    'Sk 3: Lingkungan Ideal (Info+CBT)': {'stressor': 0.2, 'cbt': 0.8, 'information': 0.9, 'prospect': 0.7},
    'Sk 4: Mismatch Minat-Kemampuan': {'stressor': 0.5, 'cbt': 0.5, 'information': 0.5, 'prospect': 0.2},
}

st.sidebar.header(" Konfigurasi Perbandingan")
n_iters = st.sidebar.slider("Jumlah Iterasi per Skenario (N)", 10, 200, 30, 10)
n_steps = 50

# Cache fungsi agar tidak meload ulang terus menerus saat filter diganti
@st.cache_data(show_spinner=False)
def run_comparison(iters, steps):
    data = []
    for sc_name, params in SCENARIOS.items():
        for it in range(iters):
            m = MajorSelectionModel(
                n_agents=30, width=10, height=10,
                stressor=params['stressor'], cbt=params['cbt'],
                information=params['information'], prospect=params['prospect'],
                seed=it
            )
            m.run(steps)
            df = m.datacollector.get_model_vars_dataframe()
            dist = m.get_state_distribution()
            
            data.append({
                'Skenario': sc_name,
                'Iterasi': it,
                'Stressor': params['stressor'],
                'CBT': params['cbt'],
                'Informasi': params['information'],
                'Prospek': params['prospect'],
                'Avg_Anxiety': df['Avg_C'].iloc[-1],
                'Avg_Score': df['Avg_Score'].iloc[-1],
                'Pct_Yakin': (dist['Yakin'] / 30) * 100,
                'Pct_Salah': (dist['Salah'] / 30) * 100
            })
    return pd.DataFrame(data)

if st.sidebar.button(" Jalankan Perbandingan Skenario", type="primary", use_container_width=True):
    with st.spinner(f"Menjalankan {len(SCENARIOS) * n_iters} total simulasi komparatif. Harap tunggu..."):
        df_comp = run_comparison(n_iters, n_steps)
        st.session_state.df_comp = df_comp

# --- OUTPUT HASIL KOMPARASI ---
if 'df_comp' in st.session_state:
    df = st.session_state.df_comp
    
    # Agregasi data
    df_agg = df.groupby('Skenario').agg({
        'Avg_Anxiety': ['mean', 'std'],
        'Avg_Score': ['mean', 'std'],
        'Pct_Yakin': 'mean',
        'Pct_Salah': 'mean',
        'Stressor': 'first',
        'CBT': 'first',
        'Informasi': 'first',
        'Prospek': 'first'
    }).reset_index()
    
    # Meratakan struktur multi-index columns
    df_agg.columns = ['Skenario', 'Mean_Anxiety', 'Std_Anxiety', 'Mean_Score', 'Std_Score', 
                      'Pct_Yakin', 'Pct_Salah', 'Stressor', 'CBT', 'Informasi', 'Prospek']
    
    # Tambahkan kalkulasi 95% Confidence Interval (CI)
    df_agg['CI_Anxiety'] = 1.96 * df_agg['Std_Anxiety'] / math.sqrt(n_iters)
    
    st.markdown("---")
    st.subheader(" Grouped Bar Chart Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Grouped Bar: Persentase Yakin vs Salah
        df_melt = pd.melt(df_agg, id_vars=['Skenario'], value_vars=['Pct_Yakin', 'Pct_Salah'],
                          var_name='Tipe', value_name='Persentase')
        fig_bar = px.bar(df_melt, x='Skenario', y='Persentase', color='Tipe', barmode='group',
                         color_discrete_map={'Pct_Yakin': '#27AE60', 'Pct_Salah': '#E74C3C'},
                         title='Persentase Status Agen (Yakin vs Salah) antar Skenario')
        fig_bar.update_layout(template="plotly_dark", xaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        # Bar chart with Error Bars for Average Anxiety
        fig_err = px.bar(df_agg, x='Skenario', y='Mean_Anxiety', error_y='CI_Anxiety',
                         color='Skenario', title='Average Anxiety dengan 95% Confidence Interval')
        fig_err.update_layout(template="plotly_dark", xaxis_title="")
        st.plotly_chart(fig_err, use_container_width=True)

    st.markdown("---")
    st.subheader(" Analisis Multivariabel (Radar Chart & Heatmap)")
    
    col3, col4 = st.columns([1.2, 1])
    with col3:
        # Radar Chart
        categories = ['Stressor', 'CBT', 'Informasi', 'Prospek', 'Mean_Anxiety', 'Mean_Score']
        fig_radar = go.Figure()
        
        for i, row in df_agg.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row['Stressor'], row['CBT'], row['Informasi'], row['Prospek'], row['Mean_Anxiety'], row['Mean_Score']],
                theta=categories,
                fill='toself',
                name=row['Skenario']
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            title='Karakteristik & Kinerja Model per Skenario',
            template="plotly_dark"
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col4:
        # Heatmap Korelasi Hasil
        # Skalakan beberapa metrik ke rentang 0-1 untuk visualisasi heatmap yang rapi
        df_heat = df_agg.set_index('Skenario')[['Pct_Yakin', 'Pct_Salah', 'Mean_Anxiety', 'Mean_Score']].copy()
        df_heat['Pct_Yakin'] /= 100
        df_heat['Pct_Salah'] /= 100
        
        fig_heat = px.imshow(df_heat, text_auto=".2f", aspect="auto", 
                             color_continuous_scale="RdYlBu_r",
                             title="Heatmap Kinerja Skenario (Skala 0-1)")
        fig_heat.update_layout(template="plotly_dark")
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("---")
    st.subheader(" Parallel Coordinates")
    st.write("Analisis hubungan antar banyak variabel sekaligus dari seluruh raw data simulasi.")
    
    # Map Skenario ke variabel ID numerik (agar bisa diberi warna di Parallel Coordinates)
    df['Sc_ID'] = df['Skenario'].astype('category').cat.codes
    
    fig_parallel = px.parallel_coordinates(
        df, color="Sc_ID",
        dimensions=['Stressor', 'CBT', 'Informasi', 'Avg_Anxiety', 'Avg_Score', 'Pct_Yakin'],
        color_continuous_scale=px.colors.diverging.Tealrose,
        title="Jalur Parameter (Stressor/CBT/Info) terhadap Hasil Akhir (Anxiety/Score/Yakin)"
    )
    fig_parallel.update_layout(template="plotly_dark")
    st.plotly_chart(fig_parallel, use_container_width=True)
    
else:
    st.info(" Konfigurasikan parameter sampel di Sidebar dan tekan tombol **'Jalankan Perbandingan Skenario'**.")
