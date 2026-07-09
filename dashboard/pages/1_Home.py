import streamlit as st

st.set_page_config(page_title="Home - ABM Simulasi", layout="wide")

st.title(" Beranda Proyek Penelitian")
st.markdown("---")

st.header("Simulasi Pengambilan Keputusan Pemilihan Jurusan Kuliah Menggunakan Agent-Based Modeling (ABM)")

st.markdown("""
###  Tujuan Penelitian & Dashboard
Dashboard ini dibangun sebagai perangkat **eksplorasi saintifik** bagi akademisi, peneliti, dan pengambil kebijakan (seperti guru BK atau pihak universitas). 
Melalui perangkat lunak ini, Anda tidak hanya melihat hasil akhir, melainkan dapat **mengubah langsung parameter-parameter lingkungan** (seperti *Stressor*, Informasi, dan Dukungan Konseling/CBT) untuk melihat bagaimana perilaku populasi calon mahasiswa beradaptasi dan berubah secara *real-time*.

###  Spesifikasi Model Default
- **Jumlah Agent**: 30 Agent (Setiap agent merepresentasikan satu calon mahasiswa)
- **Time Steps**: 50 putaran waktu simulasi (bisa disesuaikan)
- **Iterasi Monte Carlo**: 1000 iterasi per skenario (Tersedia di Menu Monte Carlo)
- **Atribut Dinamis Agent**:
    1. **Minat (M)**
    2. **Kemampuan (K)**
    3. **Pengaruh Sosial (Sos)**
    4. **Tingkat Kecemasan/Kebingungan (C)**

###  Framework & Teknologi yang Digunakan
- **Logika Inti**: Python, Mesa Framework (ABM Engine)
- **Analisis Data**: Pandas, NumPy
- **Antarmuka & Visualisasi**: Streamlit (Multipage), Plotly (Interaktif)

""")

st.success("Gunakan navigasi Sidebar di sisi kiri untuk menjalankan simulasi atau mengeksplorasi data.")
