import streamlit as st
import threading
from Flask_server import run_flask
from AI import get_gpt_response, text_to_speech, send_audio_to_esp32
import os

# Start Flask server in background
if 'flask_started' not in st.session_state:
    threading.Thread(target=run_flask, daemon=True).start()
    st.session_state.flask_started = True

# STREAMLIT UI
st.title("GPT-3.5 to TTS with ESP32")

user_input = st.text_input("Enter your prompt")

if st.button("Send"):
    if user_input:
        gpt_response = get_gpt_response(user_input)
        st.write("GPT Response:", gpt_response)
        audio_file = text_to_speech(gpt_response)
        st.audio(audio_file, format='audio/mp3')
        response = send_audio_to_esp32(audio_file)
        if response and response.status_code == 200:
            st.success("Audio berhasil dikirim ke ESP32!")
        else:
            st.error("Gagal mengirim audio ke ESP32.")
        os.unlink(audio_file)
    else:
        st.warning("Silakan isi prompt terlebih dahulu.")
