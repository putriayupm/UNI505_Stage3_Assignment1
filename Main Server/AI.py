import os
import tempfile
import requests
from openai import OpenAI
from gtts import gTTS
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def get_gpt_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Kamu adalah guru SD yang ramah dan profesional. "
                        "Jawablah dengan singkat, sopan, dan sesuai untuk anak-anak. "
                        "Jangan mengandung kekerasan, bahasa kasar, atau konten tidak pantas."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=30
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Gagal mendapatkan respons GPT: {str(e)}")
        return ""

def text_to_speech(text):
    tts = gTTS(text=text, lang='id', slow=False)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
        tts.save(temp_file.name)
        return temp_file.name

def send_audio_to_esp32(audio_file_path):
    url = "http://172.20.10.3/play_audio"
    try:
        with open(audio_file_path, 'rb') as audio_file:
            files = {'file': ('audio.mp3', audio_file, 'audio/mp3')}
            response = requests.post(url, files=files)
        return response
    except Exception as e:
        st.error(f"Error sending audio: {str(e)}")
        return None
