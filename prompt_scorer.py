import streamlit as st
import openai
from typing import Dict, List, Tuple
import json
import os
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
st.set_page_config(
    page_title=os.getenv("APP_TITLE", "Penilai Prompt Engineering"),
    page_icon="🎯",
    layout="wide"
)

# Teknik Prompt Engineering
class TeknikPrompt(Enum):
    ZERO_SHOT = "Zero-Shot"
    FEW_SHOT = "Few-Shot"
    CHAIN_OF_THOUGHT = "Chain of Thought"
    TREE_OF_THOUGHTS = "Tree of Thoughts"

@dataclass
class AnalisisPrompt:
    skor: int
    jenis_tugas: str
    teknik_sesuai: List[str]
    teknik_ditemukan: List[str]
    teknik_disarankan: List[str]
    kelebihan: List[str]
    kekurangan: List[str]
    rekomendasi: List[str]
    versi_perbaikan: str

class PenilaiPrompt:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY tidak ditemukan di .env file")
        self.client = openai.OpenAI(api_key=api_key)
        
    def analisis_prompt(self, prompt: str) -> AnalisisPrompt:
        """Analisis prompt berdasarkan konteks penggunaan"""
        
        prompt_analisis = f"""
        Analisis prompt berikut berdasarkan 4 teknik utama prompt engineering:
        
        1. Zero-Shot: Instruksi langsung tanpa contoh
        2. Few-Shot: Menyertakan contoh untuk panduan format/output
        3. Chain of Thought: Meminta reasoning step-by-step
        4. Tree of Thoughts: Eksplorasi multiple paths/opsi
        
        Berikan respons dalam format JSON:
        {{
            "skor": <0-100>,
            "jenis_tugas": "<kategorisasi tugas>",
            "teknik_sesuai": ["teknik yang cocok untuk jenis tugas ini"],
            "teknik_ditemukan": ["teknik yang sudah digunakan"],
            "teknik_disarankan": ["teknik yang sebaiknya ditambahkan"],
            "kelebihan": ["poin kuat prompt"],
            "kekurangan": ["poin lemah prompt"],
            "rekomendasi": ["saran perbaikan spesifik"],
            "versi_perbaikan": "prompt yang sudah diperbaiki"
        }}
        
        Kriteria penilaian:
        - Kesesuaian teknik dengan jenis tugas (40%)
        - Kejelasan instruksi (30%)
        - Struktur dan organisasi (20%)
        - Kelengkapan konteks (10%)
        
        PENTING: Sesuaikan teknik dengan kebutuhan. Tidak semua prompt butuh teknik kompleks.
        
        Prompt yang dianalisis:
        \"\"\"
        {prompt}
        \"\"\"
        
        Respons dalam bahasa Indonesia.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=[
                    {"role": "system", "content": "Kamu adalah ahli prompt engineering yang fokus pada 4 teknik utama: Zero-Shot, Few-Shot, Chain of Thought, dan Tree of Thoughts. Evaluasi berdasarkan kesesuaian teknik dengan kebutuhan."},
                    {"role": "user", "content": prompt_analisis}
                ],
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return AnalisisPrompt(
                skor=result["skor"],
                jenis_tugas=result["jenis_tugas"],
                teknik_sesuai=result["teknik_sesuai"],
                teknik_ditemukan=result["teknik_ditemukan"],
                teknik_disarankan=result["teknik_disarankan"],
                kelebihan=result["kelebihan"],
                kekurangan=result["kekurangan"],
                rekomendasi=result["rekomendasi"],
                versi_perbaikan=result["versi_perbaikan"]
            )
            
        except Exception as e:
            st.error(f"Error saat menganalisis prompt: {str(e)}")
            st.info("Pastikan OPENAI_API_KEY sudah diset di file .env")
            return None

def tampilkan_meter_skor(skor: int):
    """Tampilkan meter skor visual"""
    if skor < 50:
        status = "Perlu Perbaikan 🔴"
        color = "red"
    elif skor < 75:
        status = "Cukup Baik 🟡"
        color = "orange"
    else:
        status = "Sangat Baik 🟢"
        color = "green"
    
    st.markdown(f"""
    <div style="text-align: center;">
        <h2 style="color: {color};">{skor}/100</h2>
        <p>{status}</p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(skor / 100)

def main():
    st.title("🎯 Penilai Prompt Engineering")
    st.markdown("Analisis dan tingkatkan prompt Anda dengan AI")
    
    # Check API key
    try:
        penilai = PenilaiPrompt()
    except ValueError as e:
        st.error("❌ OPENAI_API_KEY tidak ditemukan!")
        st.info("""
        📝 Cara setup:
        1. Buat file `.env` di folder yang sama
        2. Tambahkan: `OPENAI_API_KEY=your-api-key-here`
        3. Restart aplikasi
        """)
        return
    
    
    # Main input section
    st.header("📝 Masukkan Prompt Anda")
    
    # Example buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Zero-Shot", use_container_width=True):
            st.session_state.sample = "Jelaskan konsep blockchain dalam 3 paragraf untuk pemula."
    
    with col2:
        if st.button("Few-Shot", use_container_width=True):
            st.session_state.sample = """Ubah deskripsi produk menjadi caption Instagram yang menarik.

Contoh 1:
Produk: Tas kanvas ramah lingkungan
Caption: Eco-friendly canvas bag 🌱 Style meets sustainability! Perfect untuk daily adventures. #EcoFashion #SustainableLiving

Contoh 2:
Produk: Botol minum stainless steel
Caption: Stay hydrated in style! 💧 Our stainless steel bottle keeps drinks cold for 24hrs. #Hydration #EcoFriendly

Sekarang buatkan untuk:
Produk: Sepatu sneakers dari bahan daur ulang"""
    
    with col3:
        if st.button("Chain of Thought", use_container_width=True):
            st.session_state.sample = """Saya punya budget Rp 5.000.000 untuk liburan 4 hari 3 malam di Bali untuk 2 orang. 

Bantu saya buat rencana budget detail. Pikirkan step by step:
1. Hitung alokasi untuk setiap kategori (transport, hotel, makan, aktivitas)
2. Cari opsi yang sesuai budget untuk setiap kategori
3. Hitung total dan pastikan tidak melebihi budget
4. Berikan rekomendasi final dengan breakdown biaya"""

    with col4:
        if st.button("Tree of Thoughts", use_container_width=True):
            st.session_state.sample = """Saya ingin memulai bisnis online dengan modal Rp 10 juta. 

Eksplorasi 3 ide bisnis yang berbeda:
1. E-commerce fashion
2. Kursus online
3. Jasa digital marketing

Untuk setiap ide:
- Jelaskan konsep bisnis
- Breakdown modal yang dibutuhkan
- Analisis target market
- Proyeksi revenue 6 bulan
- List risiko dan mitigasi

Berikan rekomendasi bisnis mana yang paling potensial."""
    
    # Text area
    prompt_pengguna = st.text_area(
        "",
        height=250,
        value=st.session_state.get('sample', ''),
        placeholder="Paste prompt Anda di sini..."
    )
    
    # Analyze button
    if st.button("🔍 Analisis Prompt", type="primary", use_container_width=True):
        if not prompt_pengguna:
            st.error("❌ Silakan masukkan prompt terlebih dahulu")
            return
            
        with st.spinner("Sedang menganalisis prompt..."):
            analisis = penilai.analisis_prompt(prompt_pengguna)
            
        if analisis:
            st.markdown("---")
            
            # Results header
            st.header("📊 Hasil Analisis")
            
            # Score and task type
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.info(f"**📌 Jenis Tugas:** {analisis.jenis_tugas}")
            
            with col2:
                tampilkan_meter_skor(analisis.skor)
            
            with col3:
                st.info(f"**🎯 Teknik Sesuai:** {', '.join(analisis.teknik_sesuai)}")
            
            # Technique analysis
            st.subheader("🔍 Analisis Teknik")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Teknik yang Ditemukan:**")
                if analisis.teknik_ditemukan:
                    for teknik in analisis.teknik_ditemukan:
                        st.success(f"• {teknik}")
                else:
                    st.warning("• Belum ada teknik spesifik")
            
            with col2:
                st.markdown("**💡 Teknik yang Disarankan:**")
                if analisis.teknik_disarankan:
                    for teknik in analisis.teknik_disarankan:
                        st.info(f"• {teknik}")
                else:
                    st.success("• Teknik sudah optimal!")
            
            # Detailed feedback
            st.subheader("💬 Feedback Detail")
            
            tab1, tab2, tab3 = st.tabs(["✅ Kelebihan", "⚠️ Kekurangan", "🎯 Rekomendasi"])
            
            with tab1:
                for item in analisis.kelebihan:
                    st.markdown(f"• {item}")
            
            with tab2:
                if analisis.kekurangan:
                    for item in analisis.kekurangan:
                        st.markdown(f"• {item}")
                else:
                    st.success("Tidak ada kekurangan signifikan!")
            
            with tab3:
                for item in analisis.rekomendasi:
                    st.markdown(f"• {item}")
            
            # Improved version
            st.subheader("🚀 Versi yang Disarankan")
            
            # Show improved prompt
            st.code(analisis.versi_perbaikan, language="text")
            
            # Comparison toggle
            if st.checkbox("📊 Lihat perbandingan Before/After"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**❌ Before (Original):**")
                    st.text_area("", prompt_pengguna, height=300, disabled=True, key="original")
                
                with col2:
                    st.markdown("**✅ After (Improved):**")
                    st.text_area("", analisis.versi_perbaikan, height=300, disabled=True, key="improved")
            
            # Success message
            st.success("✅ Analisis selesai! Gunakan versi yang disarankan untuk hasil yang lebih baik.")

if __name__ == "__main__":
    main()