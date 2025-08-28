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

# Configuration - Streamlit Cloud compatible
def get_config():
    """Get configuration from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        return {
            "api_key": st.secrets["openai"]["api_key"],
            "model": st.secrets["openai"]["model"],
            "temperature": st.secrets["openai"]["temperature"],
            "app_title": st.secrets["app"]["title"],
            "app_debug": st.secrets["app"]["debug"]
        }
    except (KeyError, FileNotFoundError):
        # Fallback to environment variables (for local development)
        return {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-4"),
            "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.3")),
            "app_title": os.getenv("APP_TITLE", "Penilai Prompt Engineering"),
            "app_debug": os.getenv("APP_DEBUG", "False").lower() == "true"
        }

config = get_config()

st.set_page_config(
    page_title=config["app_title"],
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
class TeknikInfo:
    teknik: str
    alasan: str

@dataclass
class AnalisisPrompt:
    skor: int
    jenis_tugas: str
    teknik_sesuai: List[str]
    teknik_ditemukan: List[TeknikInfo]
    teknik_disarankan: List[TeknikInfo]
    kelebihan: List[str]
    kekurangan: List[str]
    rekomendasi: List[str]
    versi_perbaikan: str

class PenilaiPrompt:
    def __init__(self):
        api_key = config["api_key"]
        if not api_key:
            raise ValueError("OPENAI_API_KEY tidak ditemukan")
        self.client = openai.OpenAI(api_key=api_key)
        
    def analisis_prompt(self, prompt: str) -> AnalisisPrompt:
        """Analisis prompt berdasarkan konteks penggunaan"""
        
        prompt_analisis = f"""
        Kamu adalah evaluator prompt engineering yang sangat berpengalaman dan detail. Analisis prompt berikut dengan standar profesional yang tinggi.

        FRAMEWORK EVALUASI:
        
        1. CLARITY & SPECIFICITY (25 poin):
           - Apakah tujuan jelas dan spesifik? 
           - Apakah instruksi mudah dipahami?
           - Apakah ada ambiguitas yang bisa membingungkan AI?
        
        2. CONTEXT & BACKGROUND (20 poin):
           - Apakah konteks cukup untuk AI memahami situasi?
           - Apakah ada informasi penting yang hilang?
           - Apakah target audience/use case jelas?
        
        3. STRUCTURE & ORGANIZATION (20 poin):
           - Apakah prompt terstruktur dengan baik?
           - Apakah ada logical flow yang jelas?
           - Apakah format output ditentukan dengan jelas?
        
        4. TECHNIQUE APPROPRIATENESS (20 poin):
           - Apakah teknik prompt engineering yang digunakan sesuai dengan jenis tugas?
           - Zero-Shot: Untuk tugas sederhana/umum
           - Few-Shot: Untuk format/style specific tasks  
           - Chain of Thought: Untuk reasoning/problem solving
           - Tree of Thoughts: Untuk creative/exploratory tasks
        
        5. COMPLETENESS & CONSTRAINTS (15 poin):
           - Apakah semua parameter/constraints sudah disebutkan?
           - Apakah ada guardrails untuk mencegah output yang tidak diinginkan?
           - Apakah length/format requirements jelas?
        
        PENILAIAN YANG REALISTIS:
        - Skor 90-100: Exceptional - hampir tidak ada yang perlu diperbaiki
        - Skor 80-89: Very Good - minor improvements saja
        - Skor 70-79: Good - beberapa area perlu diperbaiki
        - Skor 60-69: Fair - cukup banyak yang bisa ditingkatkan
        - Skor 50-59: Poor - banyak masalah fundamental
        - Skor <50: Very Poor - perlu dirombak total
        
        Berikan feedback yang:
        1. KONSTRUKTIF - fokus pada solusi, bukan hanya kritik
        2. ACTIONABLE - berikan langkah konkret untuk perbaikan
        3. BALANCED - sebutkan apa yang sudah baik sebelum kritik
        4. SPECIFIC - hindari feedback generic, berikan contoh konkret
        
        Berikan respons dalam format JSON:
        {{
            "skor": <0-100, berdasarkan framework di atas>,
            "jenis_tugas": "<kategorisasi spesifik: creative writing, data analysis, code generation, problem solving, etc>",
            "teknik_sesuai": ["teknik yang paling cocok untuk jenis tugas ini"],
            "teknik_ditemukan": [
                {{
                    "teknik": "nama teknik",
                    "alasan": "penjelasan spesifik mengapa terdeteksi sebagai teknik ini, dengan kutipan bagian prompt yang relevan"
                }}
            ],
            "teknik_disarankan": [
                {{
                    "teknik": "nama teknik yang disarankan",
                    "alasan": "penjelasan mengapa teknik ini akan meningkatkan hasil, dan bagaimana implementasinya"
                }}
            ],
            "kelebihan": ["poin kuat yang sudah bagus - sebutkan dengan spesifik"],
            "kekurangan": ["masalah konkret yang perlu diperbaiki - dengan penjelasan"],
            "rekomendasi": ["3-4 saran improvement yang paling impactful"],
            "versi_perbaikan": "prompt yang sudah diperbaiki dengan menerapkan rekomendasi"
        }}
        
        PENTING untuk teknik_disarankan:
        - Jika teknik yang disarankan SUDAH digunakan dengan baik dalam prompt, berikan pujian dan jelaskan bahwa teknik tersebut sudah optimal
        - Jika teknik belum digunakan, berikan saran konkret bagaimana mengimplementasikannya
        - Jangan menyarankan teknik yang sudah ada kecuali perlu peningkatan
        
        Prompt yang dianalisis:
        \"\"\"
        {prompt}
        \"\"\"
        
        Berikan evaluasi yang honest dan membangun dalam bahasa Indonesia.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": "Kamu adalah senior prompt engineering evaluator dengan pengalaman 10+ tahun. Berikan penilaian yang profesional, objektif, dan konstruktif. Fokus pada detail teknis yang konkret dan actionable insights. Jangan terlalu murah memberikan skor tinggi - gunakan standar industri yang ketat. Bahasa tetap ramah tapi profesional dan to-the-point."},
                    {"role": "user", "content": prompt_analisis}
                ],
                temperature=config["temperature"],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse teknik_ditemukan and teknik_disarankan
            teknik_ditemukan = [
                TeknikInfo(teknik=item["teknik"], alasan=item["alasan"]) 
                for item in result["teknik_ditemukan"]
            ] if result["teknik_ditemukan"] else []
            
            teknik_disarankan = [
                TeknikInfo(teknik=item["teknik"], alasan=item["alasan"]) 
                for item in result["teknik_disarankan"]
            ] if result["teknik_disarankan"] else []
            
            return AnalisisPrompt(
                skor=result["skor"],
                jenis_tugas=result["jenis_tugas"],
                teknik_sesuai=result["teknik_sesuai"],
                teknik_ditemukan=teknik_ditemukan,
                teknik_disarankan=teknik_disarankan,
                kelebihan=result["kelebihan"],
                kekurangan=result["kekurangan"],
                rekomendasi=result["rekomendasi"],
                versi_perbaikan=result["versi_perbaikan"]
            )
            
        except Exception as e:
            st.error(f"Error saat menganalisis prompt: {str(e)}")
            st.info("Pastikan OPENAI_API_KEY sudah diset dengan benar")
            return None

def generate_tips_kilat(analisis: AnalisisPrompt, client, prompt_asli: str) -> List[str]:
    """Generate tips kilat berdasarkan analisis AI dan prompt asli"""
    prompt_tips = f"""
    Berdasarkan evaluasi prompt berikut:

    PROMPT ASLI:
    \"\"\"{prompt_asli}\"\"\"

    HASIL ANALISIS:
    - Skor: {analisis.skor}/100
    - Jenis tugas: {analisis.jenis_tugas}
    - Teknik ditemukan: {', '.join([t.teknik for t in analisis.teknik_ditemukan]) if analisis.teknik_ditemukan else 'Tidak ada'}
    - Teknik disarankan: {', '.join([t.teknik for t in analisis.teknik_disarankan]) if analisis.teknik_disarankan else 'Tidak ada'}
    - Kekurangan utama: {'; '.join(analisis.kekurangan[:3]) if analisis.kekurangan else 'Tidak ada'}

    Berikan 3-4 rekomendasi perbaikan yang:
    1. SPESIFIK untuk prompt ini - jangan generic
    2. ACTIONABLE - bisa langsung diterapkan
    3. PRIORITAS TINGGI - fokus pada perbaikan yang paling berdampak
    4. KONTEKSTUAL - sesuai dengan jenis tugas dan tujuan prompt

    Format: satu rekomendasi per baris, mulai dengan emoji yang relevan.
    Gunakan bahasa profesional tapi tetap mudah dipahami.
    
    Contoh format yang diinginkan:
    🎯 Tambahkan definisi spesifik tentang "analisis mendalam" - sebutkan aspek apa saja yang harus dianalisis
    📝 Spesifikasi format output dengan struktur yang jelas (bullets, numbered list, atau paragraf)

    Respons hanya berupa list rekomendasi, tanpa penjelasan tambahan.
    """
    
    try:
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "system", "content": "Kamu adalah guru prompt engineering yang memberikan tips praktis dan spesifik. Berikan tips yang actionable dan mudah dipahami."},
                {"role": "user", "content": prompt_tips}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        tips_text = response.choices[0].message.content
        tips = [tip.strip() for tip in tips_text.split('\n') if tip.strip() and not tip.strip().startswith('#')]
        return tips[:4]  # Maximum 4 tips
        
    except Exception as e:
        # Fallback ke tips default jika API error
        if analisis.skor < 30:
            return [
                "🎯 Jelasin tujuan kamu lebih detail biar AI paham maksudnya",
                "📝 Kasih instruksi yang step-by-step, biar AI gak bingung",
                "🌟 Tambahin konteks yang lebih lengkap untuk hasil yang lebih baik"
            ]
        elif analisis.skor < 50:
            return [
                "📋 Tambahin 1-2 contoh biar AI tau persis yang kamu mau",
                "🧠 Minta AI jelasin 'langkah demi langkah'",
                "📐 Tentuin format output yang spesifik"
            ]
        elif analisis.skor < 75:
            return [
                "🎭 Kasih peran ke AI (misal: 'Kamu adalah ahli marketing')",
                "🌳 Minta AI pertimbangkan beberapa opsi",
                "✨ Sebutin tone yang diinginkan"
            ]
        else:
            return [
                "👑 Pertahanin konsistensi struktur yang udah bagus ini",
                "🔮 Coba eksplorasi teknik lanjutan",
                "💡 Eksperimen dengan variasi yang lebih kompleks"
            ]

def tampilkan_rekomendasi_cepat(analisis: AnalisisPrompt, penilai, prompt_asli: str):
    """Tampilkan rekomendasi cepat berdasarkan analisis AI"""
    st.subheader("💡 Rekomendasi Utama")
    
    # Determine status message based on score
    if analisis.skor < 50:
        st.warning("🔧 **Perlu Perbaikan Mendasar** - Mari kita tingkatkan prompt Anda:")
    elif analisis.skor < 65:
        st.info("📈 **Cukup Baik, Bisa Lebih Optimal** - Beberapa area untuk diperbaiki:")
    elif analisis.skor < 80:
        st.success("✅ **Sudah Bagus!** - Beberapa penyesuaian untuk hasil yang lebih maksimal:")
    else:
        st.success("🎯 **Excellent!** - Prompt Anda sudah sangat baik, sedikit finishing touch:")
    
    # Generate and display tips
    tips = generate_tips_kilat(analisis, penilai.client, prompt_asli)
    for tip in tips:
        st.markdown(f"• {tip}")

def tampilkan_meter_skor(skor: int):
    """Tampilkan meter skor visual dengan gaya profesional"""
    if skor < 50:
        status = "Perlu Peningkatan"
        color = "#ff6b6b"
        pesan = "Ada ruang besar untuk pengembangan"
    elif skor < 65:
        status = "Cukup Baik"
        color = "#ffa500"
        pesan = "Fundamen baik, butuh optimisasi"
    elif skor < 80:
        status = "Bagus"
        color = "#4ecdc4"
        pesan = "Kualitas solid, beberapa area bisa diperbaiki"
    elif skor < 90:
        status = "Sangat Bagus"
        color = "#45b7d1"
        pesan = "Kualitas tinggi, hampir optimal"
    else:
        status = "Excellent"
        color = "#96ceb4"
        pesan = "Kualitas exceptional, siap production"
        if skor >= 95:
            st.balloons()
    
    st.markdown(f"""
    <div style="text-align: center;">
        <h2 style="color: {color}; font-weight: 600;">{skor}/100</h2>
        <p style="font-weight: bold; font-size: 18px; color: {color};">{status}</p>
        <p style="font-style: italic; color: #666;">{pesan}</p>
    </div>
    """, unsafe_allow_html=True)
    st.progress(skor / 100)

def main():
    st.title("🎯 Evaluator Prompt Engineering")
    st.markdown("Analisis mendalam dan tingkatkan kualitas prompt Anda dengan standar industri profesional.")
    
    # Check API key
    try:
        penilai = PenilaiPrompt()
    except ValueError as e:
        st.error("⚠️ API Key belum dikonfigurasi")
        st.info("""
        **Untuk Streamlit Cloud:**
        1. Masuk ke Settings > Secrets di dashboard Streamlit
        2. Tambahkan konfigurasi TOML sesuai dokumentasi
        3. Deploy ulang aplikasi
        
        **Untuk Development Lokal:**
        1. Buat file `.env` di direktori project
        2. Tambahkan: `OPENAI_API_KEY=your-api-key`
        3. Restart aplikasi
        """)
        return
    
    # Main input section
    st.header("📝 Input Prompt untuk Evaluasi")
    
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
        placeholder="Masukkan prompt Anda di sini untuk evaluasi mendalam..."
    )
    
    # Analyze button
    if st.button("🔍 Mulai Evaluasi Prompt", type="primary", use_container_width=True):
        if not prompt_pengguna:
            st.error("⚠️ Silakan masukkan prompt terlebih dahulu")
            return
            
        with st.spinner("Sedang melakukan evaluasi mendalam terhadap prompt Anda..."):
            analisis = penilai.analisis_prompt(prompt_pengguna)
            
        if analisis:
            st.markdown("---")
            
            # Quick recommendations first
            tampilkan_rekomendasi_cepat(analisis, penilai, prompt_pengguna)
            
            st.markdown("---")
            
            # Results header
            st.header("📊 Hasil Evaluasi Prompt")
            
            # Score and task type
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.info(f"**📌 Kategori Tugas:** {analisis.jenis_tugas}")
            
            with col2:
                tampilkan_meter_skor(analisis.skor)
            
            with col3:
                st.info(f"**🎯 Teknik yang Direkomendasikan:** {', '.join(analisis.teknik_sesuai)}")
            
            # Technique analysis
            st.subheader("🔍 Analisis Teknik Prompt Engineering")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Teknik yang Teridentifikasi:**")
                if analisis.teknik_ditemukan:
                    for teknik_info in analisis.teknik_ditemukan:
                        with st.expander(f"📋 {teknik_info.teknik}", expanded=False):
                            st.write(f"**Alasan:** {teknik_info.alasan}")
                else:
                    st.warning("• Belum menggunakan teknik spesifik")
            
            with col2:
                st.markdown("**💡 Teknik yang Disarankan:**")
                if analisis.teknik_disarankan:
                    for teknik_info in analisis.teknik_disarankan:
                        # Check if this is praise (technique already used well) or suggestion
                        if any(dt.teknik.lower() == teknik_info.teknik.lower() for dt in analisis.teknik_ditemukan):
                            with st.expander(f"🎉 {teknik_info.teknik} (Sudah Baik!)", expanded=False):
                                st.success(f"**Pujian:** {teknik_info.alasan}")
                        else:
                            with st.expander(f"🔧 {teknik_info.teknik}", expanded=False):
                                st.info(f"**Saran:** {teknik_info.alasan}")
                else:
                    st.success("• Penggunaan teknik sudah optimal")
            
            # Detailed feedback
            st.subheader("📋 Evaluasi Detail")
            
            tab1, tab2, tab3 = st.tabs(["✅ Kelebihan", "⚠️ Area Perbaikan", "📝 Rekomendasi"])
            
            with tab1:
                if analisis.kelebihan:
                    st.markdown("**Aspek yang sudah baik dalam prompt Anda:**")
                    for item in analisis.kelebihan:
                        st.markdown(f"• {item}")
                else:
                    st.info("Masih ada potensi pengembangan yang bisa dioptimalkan")
            
            with tab2:
                if analisis.kekurangan:
                    st.markdown("**Area yang memerlukan perbaikan:**")
                    for item in analisis.kekurangan:
                        st.markdown(f"• {item}")
                else:
                    st.success("Tidak ada kekurangan signifikan yang teridentifikasi")
            
            with tab3:
                if analisis.rekomendasi:
                    st.markdown("**Saran perbaikan untuk optimalisasi:**")
                    for item in analisis.rekomendasi:
                        st.markdown(f"• {item}")
                else:
                    st.info("Prompt sudah optimal untuk kategori tugas ini")
            
            # Improved version
            st.subheader("🚀 Prompt yang Dioptimalkan")
            
            # Show improved prompt
            st.code(analisis.versi_perbaikan, language="text")
            
            # Comparison toggle
            if st.checkbox("📊 Tampilkan perbandingan sebelum dan sesudah"):
                col1, col2 = st.columns(2)
                
                st.markdown("**Perbandingan Prompt:**")
                with col1:
                    st.markdown("**📄 Prompt Asli:**")
                    st.text_area("", prompt_pengguna, height=300, disabled=True, key="original")
                
                with col2:
                    st.markdown("**✨ Prompt Optimized:**")
                    st.text_area("", analisis.versi_perbaikan, height=300, disabled=True, key="improved")
            
            # Success message
            st.success("✅ Evaluasi selesai! Silakan gunakan versi yang telah dioptimalkan untuk hasil yang lebih baik.")

if __name__ == "__main__":
    main()