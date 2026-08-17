import streamlit as st
import os
from google import genai
import edge_tts
import asyncio



st.set_page_config(page_title="IndoBetawi TTS Generator", layout="centered", page_icon="🎙️")

st.title("🎙️ IndoBetawi Audio Generator")
st.caption("Generator Suara Khas Bahasa & Logat Indonesia/Betawi berbasis AI")

GENAI_API_KEY = st.secrets.get("GENAI_API_KEY", "")

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
    client = genai.Client()
    prompt = f"Bertindaklah sebagai ahli fonetik. Ubah teks ini agar saat dibaca TTS terdengar alami dengan logat {dialek} dan vibe {suasana}. Teks: {teks}. HANYA kembalikan teks hasil optimasi."
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    return response.text.strip()

async def generate_audio(text, voice_name, rate_str, output_filename):
    communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate_str)
    await communicate.save(output_filename)

if st.button("🎙️ Generate Audio MP3", type="primary"):
    if not teks_input.strip():
        st.warning("Silakan masukkan teks narasi terlebih dahulu!")
    else:
        with st.spinner("Memproses..."):
            teks_opt = proses_teks_dengan_gemini(teks_input, logat, vibe)
            rate_str = f"{int((tempo - 1.0) * 100):+d}%"
            voice = "id-ID-ArdiNeural" if karakter == "Pria" else "id-ID-GadisNeural"
            asyncio.run(generate_audio(teks_opt, voice, rate_str, "out.mp3"))
            st.audio("out.mp3", format="audio/mp3")
