import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Tambahkan path ke folder dashboard agar bisa import modul
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import MajorSelectionModel
from charts import plot_anxiety_trend, plot_score_trend, plot_state_distribution, plot_final_state_pie, plot_state_bar
from utils import COLORS, format_metric

st.set_page_config(page_title="Single Simulation", layout="wide")

st.title(" Single Simulation Runner")

# --- SIDEBAR CONFIGURATION ---
st.sidebar.header(" Parameter Simulasi")
n_agents = st.sidebar.slider("Jumlah Agent", 10, 100, 30, 5)
grid_width = st.sidebar.slider("Lebar Grid (X)", 5, 20, 10)
grid_height = st.sidebar.slider("Tinggi Grid (Y)", 5, 20, 10)
n_steps = st.sidebar.slider("Jumlah Step", 10, 200, 50, 10)

st.sidebar.markdown("---")
st.sidebar.subheader("Variabel Lingkungan")
stressor = st.sidebar.slider("Stressor (Tekanan)", 0.0, 1.0, 0.3, 0.1)
informasi = st.sidebar.slider("Akses Informasi", 0.0, 1.0, 0.5, 0.1)
cbt = st.sidebar.slider("Dukungan CBT", 0.0, 1.0, 0.4, 0.1)
prospek = st.sidebar.slider("Prospek Karier", 0.0, 1.0, 0.6, 0.1)
random_seed = st.sidebar.number_input("Random Seed", value=42)

# --- SESSION STATE INITIALIZATION ---
if 'model' not in st.session_state:
    st.session_state.model = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False
if 'sim_done' not in st.session_state:
    st.session_state.sim_done = False

# Tombol utama untuk reset dan mulai dari awal
if st.sidebar.button(" Initialize / Reset Model", use_container_width=True):
    st.session_state.model = MajorSelectionModel(
        n_agents=n_agents, width=grid_width, height=grid_height,
        information=informasi, prospect=prospek, stressor=stressor, cbt=cbt, seed=random_seed
    )
    st.session_state.current_step = 0
    st.session_state.sim_done = False
    st.session_state.is_playing = False

# --- GRID VISUALIZATION FUNCTION ---
def render_grid(model):
    x_coords = []
    y_coords = []
    colors = []
    texts = []
    
    for agent in model.schedule.agents:
        x_coords.append(agent.pos[0])
        y_coords.append(agent.pos[1])
        colors.append(COLORS.get(agent.state, 'gray'))
        texts.append(f"State: {agent.state}<br>C: {agent.C:.2f}<br>Score: {agent.hitung_score():.2f}")
        
    fig = go.Figure(data=go.Scatter(
        x=x_coords, y=y_coords, mode='markers',
        marker=dict(size=16, color=colors, line=dict(width=1, color='white')),
        text=texts, hoverinfo='text'
    ))
    fig.update_layout(
        title=f"Pergerakan Agent (Step {model.schedule.steps})",
        xaxis=dict(range=[-1, model.grid.width], showgrid=True, dtick=1, title="X"),
        yaxis=dict(range=[-1, model.grid.height], showgrid=True, dtick=1, title="Y"),
        width=700, height=600,
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# --- MAIN UI ---
if st.session_state.model is not None:
    st.markdown("---")
    
    # Kolom untuk menampung Kontrol dan Grid
    st.subheader(" Visualisasi Grid Interaktif")
    
    # Kontrol Animasi
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button(" Play", disabled=st.session_state.sim_done or st.session_state.is_playing, use_container_width=True):
            st.session_state.is_playing = True
            st.rerun()
    with c2:
        if st.button(" Pause", disabled=not st.session_state.is_playing, use_container_width=True):
            st.session_state.is_playing = False
            st.rerun()
    with c3:
        if st.button(" Next Step", disabled=st.session_state.sim_done or st.session_state.is_playing, use_container_width=True):
            st.session_state.model.step()
            st.session_state.current_step += 1
            if st.session_state.current_step >= n_steps:
                st.session_state.sim_done = True
            st.rerun()
            
    # Progress bar simulasi
    progress = st.progress(st.session_state.current_step / n_steps)
            
    grid_placeholder = st.empty()

    # Logika Play (Automated Steps berulang otomatis)
    if st.session_state.is_playing and not st.session_state.sim_done:
        grid_placeholder.plotly_chart(render_grid(st.session_state.model), use_container_width=True)
        time.sleep(0.15)  # Kecepatan frame
        st.session_state.model.step()
        st.session_state.current_step += 1
        
        if st.session_state.current_step >= n_steps:
            st.session_state.is_playing = False
            st.session_state.sim_done = True
            
        st.rerun()
    else:
        # Tampilkan grid statis saat pause atau selesai
        grid_placeholder.plotly_chart(render_grid(st.session_state.model), use_container_width=True)
        
    # Output Visualisasi dan Metrik setelah selesai
    if st.session_state.sim_done:
        st.success(" Simulasi Selesai! Berikut adalah hasilnya:")
        st.markdown("---")
        
        df_model = st.session_state.model.datacollector.get_model_vars_dataframe()
        dist = st.session_state.model.get_state_distribution()
        
        # 1. Metric Cards
        st.subheader(" Metrik Utama")
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Avg Anxiety Akhir", format_metric(df_model['Avg_C'].iloc[-1]), f"{df_model['Avg_C'].iloc[-1] - df_model['Avg_C'].iloc[0]:.2f}")
        mc2.metric("Avg Score Akhir", format_metric(df_model['Avg_Score'].iloc[-1]))
        mc3.metric("Total Agent", n_agents)
        mc4.metric("Intervensi CBT Aktif", int(df_model['CBT_Count'].iloc[-1]))
        
        # 2. Charts
        st.markdown("<br>", unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)
        with ch1:
            st.plotly_chart(plot_anxiety_trend(df_model), use_container_width=True)
            st.plotly_chart(plot_state_distribution(df_model), use_container_width=True)
        with ch2:
            st.plotly_chart(plot_score_trend(df_model), use_container_width=True)
            st.plotly_chart(plot_final_state_pie(dist), use_container_width=True)
            
        # 3. Bar dan Data Table
        st.markdown("---")
        ch3, ch4 = st.columns([2, 1])
        with ch3:
            st.plotly_chart(plot_state_bar(dist), use_container_width=True)
        with ch4:
            st.subheader(" Tabel Distribusi Akhir")
            df_table = pd.DataFrame(list(dist.items()), columns=['State', 'Jumlah Agent'])
            df_table['Persentase'] = (df_table['Jumlah Agent'] / n_agents * 100).apply(lambda x: f"{x:.1f}%")
            st.dataframe(df_table, use_container_width=True)
        
else:
    st.info(" Silakan atur parameter di sidebar dan klik **Initialize / Reset Model** untuk memuat simulasi.")
