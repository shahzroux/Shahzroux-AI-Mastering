import streamlit as st
import os
from engine import ShahzrouxEngine
import zipfile
from io import BytesIO

# 1. Konfigurasi Tema "Premium & Mahal"
st.set_page_config(page_title="Shahzroux AI Mastering", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .main-header { font-family: 'Helvetica Neue', sans-serif; color: #FFD700; text-align: center; font-size: 3rem; font-weight: 800; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4); }
    .sub-header { color: #888; text-align: center; font-style: italic; margin-bottom: 30px; }
    .stButton>button { background: linear-gradient(145deg, #FFD700, #B8860B); color: black !important; border-radius: 10px; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. Tajuk Utama
st.markdown('<p class="main-header">SHAHZROUX</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Pro AI Audio Post-Production • Soul of Nusantara</p>', unsafe_allow_html=True)

# 3. Sidebar untuk Kawalan
with st.sidebar:
    st.header("🎚️ Control Room")
    mode = st.radio("Mastering Mode:", ["Single Track", "Batch Album (ZIP)"])
    warmth = st.slider("Analog Warmth Intensity", 0, 100, 75)
    st.info("Sistem akan automatik mengesan 'Jiwang Detector' berdasarkan BPM lagu.")

# 4. Kawasan Upload & Proses
uploaded_files = st.file_uploader("Muat Naik Lagu Abang (WAV/FLAC/MP3)", accept_multiple_files=True)

if uploaded_files:
    st.success(f"{len(uploaded_files)} lagu berjaya dimuat naik!")
    
    if st.button("🚀 MULAKAN MASTERING"):
        mastered_paths = []
        progress_bar = st.progress(0)
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Simpan fail sementara
            temp_in = f"temp_in_{uploaded_file.name}"
            temp_out = f"mastered_{uploaded_file.name}"
            
            with open(temp_in, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Jalankan Enjin Shahzroux
            engine = ShahzrouxEngine()
            engine.process_audio(temp_in, temp_out)
            
            mastered_paths.append(temp_out)
            progress_bar.progress((i + 1) / len(uploaded_files))
            st.write(f"✅ Selesai: {uploaded_file.name}")

        # 5. Bahagian Export
        st.markdown("---")
        if mode == "Single Track":
            for path in mastered_paths:
                with open(path, "rb") as f:
                    st.download_button(f"📥 Download {path}", f, file_name=path)
        else:
            # Batch Export ke ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
                for path in mastered_paths:
                    zip_file.write(path, os.path.basename(path))
            
            st.download_button("📦 Download Semua (ZIP)", zip_buffer.getvalue(), "Album_Shahzroux_Mastered.zip")

else:
    st.info("Sila masukkan lagu untuk memulakan 'Analogue Magic'.")
