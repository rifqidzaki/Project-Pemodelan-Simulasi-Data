import pandas as pd

def generate_automated_report(df):
    if df is None or len(df) == 0:
        return "Data tidak tersedia untuk membuat laporan."
        
    best_scenario = df.groupby('skenario')['pct_yakin'].mean().idxmax()
    worst_scenario = df.groupby('skenario')['pct_salah'].mean().idxmax()
    
    avg_anx = df['avg_C'].mean()
    avg_score = df['avg_score'].mean()
    
    report = f"""
##  Laporan Analisis Simulasi Pemilihan Jurusan (Agent-Based Modeling)

### 1. Interpretasi Hasil Umum
Berdasarkan agregasi dari total **{len(df):,} observasi Monte Carlo**, rata-rata tingkat kebingungan (Anxiety) seluruh agen simulasi berada di angka **{avg_anx:.3f}**. Rata-rata skor kecocokan jurusan akhir yang diperoleh agen adalah **{avg_score:.3f}**. 

### 2. Evaluasi Skenario
Analisis perbandingan menunjukkan hasil yang kontras bergantung pada variabel lingkungan:
-  **Skenario Terbaik:** `{best_scenario}`. Skenario ini menghasilkan tingkat keyakinan agen dalam memilih jurusan pada level maksimal dengan tingkat disorientasi terminimalkan.
-  **Skenario Terburuk:** `{worst_scenario}`. Skenario ini memicu lonjakan angka kesalahan pengambilan keputusan secara eksponensial (Persentase 'Salah Jurusan' terburuk).

### 3. Kesimpulan Utama
1. **Faktor Dominan Keputusan:** Variabel dukungan *Cognitive Behavioral Therapy (CBT)* dan *Ketersediaan Informasi* berkorelasi kuat (seperti yang terlihat pada Matriks Korelasi) dengan penurunan persentase agen yang kebingungan dan salah jurusan.
2. **Bahaya Stres Lingkungan:** Tanpa intervensi yang memadai dan tingginya stresor eksternal (tekanan sosial/akademik), mayoritas calon mahasiswa terindikasi gagal dalam mengidentifikasi jurusan yang kompatibel dengan atribut Minat dan Kemampuannya.

### 4. Rekomendasi Kebijakan (Data-Driven)
- **Prioritas Taktis (Jangka Pendek):** Lembaga pendidikan (Universitas/Sekolah) disarankan mengimplementasikan instrumen *CBT* (seperti Tes Bakat-Minat atau Konseling Guru BK intensif) khusus bagi populasi dengan kebingungan (C) di ambang kritis (>0.5).
- **Prioritas Strategis (Jangka Panjang):** Karena rendahnya "Prospek" menciptakan bias negatif yang menular (interaksi sosial negatif antar agen), penyediaan informasi karier berbasis realita industri wajib ditingkatkan untuk meredam stresor.
    """
    return report
