import pandas as pd

# Kamus warna standar untuk konsistensi visualisasi
COLORS = {
    'Yakin':   '#27AE60',  # Hijau
    'Ragu':    '#F39C12',  # Kuning
    'Salah':   '#E74C3C',  # Merah
    'Bingung': '#8E44AD'   # Ungu
}

def format_metric(val):
    """Format nilai metrik menjadi 4 angka desimal untuk UI"""
    return f"{val:.4f}"
