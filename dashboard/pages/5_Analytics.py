import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Analytics", layout="wide")
st.title(" Advanced Analytics")
st.write("Eksplorasi hubungan antar variabel, matriks korelasi, dan analisis tren dari kumpulan observasi Monte Carlo.")

@st.cache_data
def load_data():
    # Load dataset hasil eksekusi 4000 iterasi yang disiapkan oleh Jupyter Notebook
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'monte_carlo_results.csv'))
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

df = load_data()

if df is not None:
    st.success(f" Berhasil memuat sumber data besar (Big Data Simulation): **{len(df):,} baris observasi**.")
    
    # 1. Summary Statistics
    st.subheader(" Descriptive Statistics")
    st.dataframe(df.describe().T, use_container_width=True)
    
    st.markdown("---")
    
    # Filter kolom numerik saja
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cols_to_drop = ['run_id']
    features = [c for c in num_cols if c not in cols_to_drop]
    
    col_a, col_b = st.columns([1, 1.2])
    
    with col_a:
        # 2. Correlation Matrix
        st.subheader(" Matriks Korelasi (Pearson)")
        st.write("Menilai seberapa kuat dan ke arah mana dua variabel saling berhubungan.")
        corr = df[features].corr()
        fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", 
                             color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
        fig_corr.update_layout(template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)
        
    with col_b:
        # 3. Scatter Plot Matrix / Hubungan Variabel
        st.subheader(" Analisis Regresi & Trend Scatter Plot")
        c1, c2 = st.columns(2)
        with c1:
            x_axis = st.selectbox("Pilih Variabel Sumbu-X", options=features, index=features.index('avg_C') if 'avg_C' in features else 0)
        with c2:
            y_axis = st.selectbox("Pilih Variabel Sumbu-Y", options=features, index=features.index('pct_salah') if 'pct_salah' in features else 1)
            
        fig_scatter = px.scatter(df, x=x_axis, y=y_axis, color="skenario" if "skenario" in df.columns else None, 
                                 trendline="ols", opacity=0.4,
                                 title=f"Korelasi Linier: {x_axis} vs {y_axis}")
        fig_scatter.update_layout(template="plotly_dark")
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    st.markdown("---")
    
    # 4. Feature Importance / Sensitivity Analysis
    st.subheader(" Analisis Sensitivitas Relatif (Pengaruh terhadap Angka Kegagalan)")
    st.write("Menilai metrik apa yang paling sensitif/mempengaruhi lonjakan **Persentase Salah Jurusan** (Berdasarkan Korelasi Absolut).")
    
    target = 'pct_salah'
    if target in features:
        # Menggunakan nilai korelasi absolut sebagai proksi sensitivitas
        importance = corr[target].drop(target).abs().sort_values(ascending=True)
        
        # Beri tanda positif atau negatif dari korelasi asli
        real_corr = corr[target].drop(target)
        colors = ['red' if real_corr[idx] > 0 else 'green' for idx in importance.index]
        
        fig_imp = go.Figure(go.Bar(
            x=importance.values,
            y=importance.index,
            orientation='h',
            marker_color=colors,
            text=[f"{val:.2f} ({'Positif' if real_corr[idx]>0 else 'Negatif'})" for idx, val in zip(importance.index, importance.values)],
            textposition='auto'
        ))
        
        fig_imp.update_layout(
            title=f"Tingkat Sensitivitas Variabel terhadap Risiko '{target}'",
            xaxis_title="Tingkat Sensitivitas (Korelasi Absolut)",
            yaxis_title="Variabel Model",
            template="plotly_dark"
        )
        st.plotly_chart(fig_imp, use_container_width=True)
        st.caption("*Indikator warna: Merah (Meningkatkan risiko salah jurusan), Hijau (Menurunkan risiko salah jurusan).*")

else:
    st.warning(" Data simulasi tidak ditemukan. Pastikan file 'monte_carlo_results.csv' tersedia di root direktori proyek.")
