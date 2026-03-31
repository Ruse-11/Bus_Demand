import streamlit as st
import matplotlib.pyplot as plt
from cv_model import count_passengers
from predict import predict_split

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Smart Bus Demand System", layout="wide")

PROJECT_NAME = "🚌 Demand-Aware Bus Dispatch System"

STOP_VIDEOS = {
    "Porur": "videos/Porur.mp4",
    "Iyyappanthangal": "videos/iyya.mp4",
    "Ramapuram": "videos/Ramapuram.mp4",
    "Valasaravakkam": "videos/Valasaravakkam.mp4"
}

# ---------------- SESSION ----------------
if "passenger_count" not in st.session_state:
    st.session_state.passenger_count = None

# ---------------- UI ----------------
st.title(PROJECT_NAME)

st.markdown("""
### 🚀 Simulation: Passenger Detection & Demand Prediction

1. 🎥 Detect passengers from video  
2. 📊 Predict route distribution using ML  
""")

# ---------------- SELECT STOP ----------------
stop = st.selectbox("📍 Select Bus Stop", list(STOP_VIDEOS.keys()))
video_path = STOP_VIDEOS[stop]

# ---------------- VIDEO ----------------
st.subheader("🎬 Bus Stop Video")

with open(video_path, "rb") as video_file:
    st.video(video_file.read())

# ---------------- CV ----------------
if st.button("▶️ Run CV Simulation", use_container_width=True):

    with st.spinner("Detecting passengers..."):
        frame_placeholder = st.empty()
        count = count_passengers(video_path, frame_placeholder)

    st.session_state.passenger_count = count
    st.success(f"✅ Passengers Detected: {count}")

# ---------------- ML ----------------
if st.session_state.passenger_count is not None:

    if st.button("📊 Process the Crowd", use_container_width=True):

        with st.spinner("Running ML prediction..."):

            try:
                result = predict_split(
                    stop=stop,
                    day="Mon",
                    time_slot="08:00-08:30",
                    total=st.session_state.passenger_count
                )
            except Exception as e:
                st.error(f"❌ Prediction Error: {e}")
                st.stop()

        total = st.session_state.passenger_count
        st.subheader("🚏 Route Distribution")
        for k, v in result.items():
            people = round((v / 100) * total)
            st.write(f"➡️ {k}: {v}%  →  {people} passengers")

        # ---------------- PIE CHART ----------------
        st.subheader("📊 Distribution")

        labels = list(result.keys())
        sizes = list(result.values())

        fig, ax = plt.subplots(figsize=(4, 4))  # smaller size
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.axis('equal')
        st.pyplot(fig, use_container_width=False)  # prevent stretching