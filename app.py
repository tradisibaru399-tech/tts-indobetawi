
asyncio
import edge_tts
import google.generativeai as genai
import os

# Konfigurasi Gemini API
GENAI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
if GENAI_API_KEY:
    genai.configure(api_key=GENAI_API_KEY)

st.set_page_config(page_title="IndoBetawi TTS Generator", layout="centered", page_icon="🗣️")

st.title("🗣️ IndoBetawi Audio Generator")
st.caption("Generator Suara khas Bahasa & Logat Indonesia/Betawi berbasis AI")

# Input Parameter Pengguna
col1, col2 = st.columns(2)
with col1:
    logat = st.selectbox("Pilihan Logat", ["Indonesia Standard", "Betawi"])
    karakter = st.selectbox("Karakter Suara", ["Pria", "Wanita"])

with col2:
    vibe = st.selectbox("Vibe / Suasana", ["Ceria", "Sedih", "Puitis", "Berwibawa", "Seram"])
    tempo = st.slider("Kecepatan Tempo Suara", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

teks_input = st.text_area("Kolom Narasi (Tanpa Batas Karakter)", height=200, placeholder="Ketik narasi Anda di sini...")

def proses_teks_dengan_gemini(teks, dialek, suasana):
    if not GENAI_API_KEY:
        return teks
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = f"""
    Bertindaklah sebagai ahli fonetik dan dialek bahasa. 
    Ubah dan optimalkan teks berikut agar saat dibaca oleh mesin TTS, hasilnya sangat alami sesuai parameter:
    - Logat: {dialek} (Jika Betawi, sesuaikan kosa kata/intonasi seperti penggunaan akhiran 'e', kata 'kagak', 'gimana', 'bisa', dll. secara pas).
    - Vibe/Suasana: {suasana} (Tambahkan tanda baca yang mendukung jeda, penekanan emosi, atau ritme).
    
    Teks Asli: "{teks}"
    
    HANYA kembalikan teks hasil optimasi fonetik tanpa penjelasan tambahan.
    """
    response = model.generate_content(prompt)
    return response.text.strip()

async def generate_audio(text, voice_name, rate_str, output_filename="output.mp3"):
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate_str)
    await communicate.save(output_filename)

VOICE_MAPPING = {
    "Pria": "id-ID-ArdiNeural",
    "Wanita": "id-ID-GadisNeural"
}

if st.button("🔊 Generate Audio MP3", type="primary"):
    if not teks_input.strip():
        st.warning("Silakan masukkan teks narasi terlebih dahulu!")
    else:
        with st.spinner("Gemini sedang menganalisis & menyesuaikan ekspresi teks..."):
            teks_teroptimasi = proses_teks_dengan_gemini(teks_input, logat, vibe)
            st.info(f"**Teks Hasil Analisis Gemini ({logat} - {vibe}):**\n\n\"{teks_teroptimasi}\"")
        
        with st.spinner("Mengubah teks menjadi audio MP3..."):
            rate_percentage = int((tempo - 1.0) * 100)
            rate_str = f"{'+' if rate_percentage >= 0 else ''}{rate_percentage}%"
            voice_selected = VOICE_MAPPING[karakter]
            output_file = "output_narasi.mp3"
            
            asyncio.run(generate_audio(teks_teroptimasi, voice_selected, rate_str, output_file))
            
            st.success("Audio berhasil dibuat!")
            st.audio(output_file, format="audio/mp3")
            
            with open(output_file, "rb") as file:
                st.download_button(
                    label="📥 Download MP3",
                    data=file,
                    file_name="indo_betawi_audio.mp3",
                    mime="audio/mp3"
                )
