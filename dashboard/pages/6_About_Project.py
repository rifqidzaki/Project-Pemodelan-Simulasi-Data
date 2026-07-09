import streamlit as st
import pandas as pd
import io
import sys
import os

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from report import generate_automated_report

st.set_page_config(page_title="Report & Export", layout="wide")
st.title(" Automatic Report & Data Export")
st.write("Fasilitas penyusunan kesimpulan cerdas dan menu pengunduhan data secara komprehensif.")

@st.cache_data
def load_data():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'monte_carlo_results.csv'))
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

df = load_data()

st.markdown("---")
# 1. Automatic Report Generation
st.subheader(" Generate Laporan Otomatis (AI Based Logic)")
st.write("Sistem akan menganalisis data, mencari metrik ekstrem (terbaik/terburuk), dan menyusun narasi laporan dalam bahasa Indonesia.")

if st.button("Generate Laporan Otomatis", type="primary"):
    with st.spinner("Menganalisis matriks big data... Menulis interpretasi..."):
        report_md = generate_automated_report(df)
        st.success("Laporan berhasil disintesis!")
        
        with st.expander("Buka Hasil Dokumen Laporan", expanded=True):
            st.markdown(report_md)
            
        # Export Laporan MD
        st.download_button(
            label=" Download Teks Laporan (.md / Document)", 
            data=report_md, 
            file_name="Laporan_Otomatis_Simulasi_Jurusan.md", 
            mime="text/markdown"
        )

st.markdown("---")

# 2. Data Export UI
st.subheader(" Modul Ekspor Data Eksternal")
st.write("Pilih ekstensi *file* untuk mengunduh log transaksi dan visualisasi dashboard.")

c1, c2, c3, c4 = st.columns(4)

if df is not None:
    # CSV
    csv = df.to_csv(index=False).encode('utf-8')
    c1.download_button(" Ekspor CSV", data=csv, file_name="ABM_Data.csv", mime="text/csv", use_container_width=True)
    
    # Excel via io.BytesIO
    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='MonteCarlo_Raw')
        c2.download_button(" Ekspor Excel (.xlsx)", data=buffer, file_name="ABM_Data.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
    except Exception as e:
        c2.error("Modul Excel (xlsxwriter) belum siap.")
        
    # PDF / PNG instructions
    c3.button(" Unduh PNG", help="Setiap grafik Plotly di dashboard ini bisa diunduh dengan cara mengarahkan kursor ke grafik dan mengklik ikon 'Kamera' (Download plot as png) di sudut kanan atas.", use_container_width=True)
    c4.button(" Cetak PDF", help="Untuk mengunduh dokumen dashboard sebagai PDF beresolusi tinggi, cukup tekan kombinasi tuts (Ctrl+P / Cmd+P) di browser web Anda lalu pilih 'Save as PDF'.", use_container_width=True)

else:
    st.warning(" Data 'monte_carlo_results.csv' tidak tersedia untuk diekspor.")

st.markdown("---")
st.subheader(" Tentang Proyek (About)")
st.info("""
Aplikasi **Streamlit Dashboard** ini dikembangkan berdasarkan riset *Agent-Based Modeling (ABM)*.
Kode modular di belakang layar terpisah secara *clean-code* ke dalam folder: `model.py`, `agent.py`, `utils.py`, `charts.py`, dan `report.py`.
""")
