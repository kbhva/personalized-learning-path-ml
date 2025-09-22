import streamlit as st
import requests
import re

st.set_page_config(
    page_title="Personalized Learning Path",
    page_icon="📚",
    layout="wide"
)

# ---------- CSS Styling ----------
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #fdfcfb, #e2d1c3);
        font-family: 'Inter', sans-serif;
    }
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 900;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #475569;
        margin-bottom: 2rem;
    }
    .card {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .card:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 28px rgba(0,0,0,0.15);
    }
    .card img {
        width: 100%;
        border-radius: 14px;
        margin-bottom: 12px;
    }
    .tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 4px 6px 4px 0;
        background: linear-gradient(90deg, #93c5fd, #3b82f6);
        color: white;
    }
    .stButton button {
        background: linear-gradient(90deg, #6366f1, #3b82f6);
        color: white;
        border-radius: 12px;
        padding: 0.7em 1.4em;
        border: none;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(90deg, #4f46e5, #1d4ed8);
        transform: scale(1.07);
        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.markdown("<h1 class='main-title'>📚 Personalized Learning Path</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Build your AI-curated journey with style 🚀</p>", unsafe_allow_html=True)

# ---------- Topics ----------
topics_order = [
    "Introduction to Python", "Data Structures", "OOP Concepts",
    "Introduction to ML", "Linear Regression", "Decision Trees", "Neural Networks"
]

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ⚙️ Customize Your Path")
    known_topic = st.selectbox("✅ Your known topic:", topics_order)
    known_idx = topics_order.index(known_topic)
    available_goal_topics = topics_order[known_idx:]
    goal_topic = st.selectbox("🎯 Your goal topic:", available_goal_topics)

    preferred_type = st.radio("🎬 Content type:", ["any", "video", "article"])
    difficulty = st.radio("🧩 Difficulty:", ["any", "easy", "medium", "hard"])
    max_length = st.slider("⏱️ Max length (minutes):", 5, 180, 45)

    generate = st.button("🚀 Generate Path")

# ---------- Thumbnail Helper ----------
def get_youtube_thumbnail(url):
    youtube_regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(youtube_regex, url)
    if match:
        video_id = match.group(1)
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return "https://via.placeholder.com/300x150.png?text=No+Preview"

# ---------- API Call ----------
if generate:
    payload = {
        "known_topic": known_topic,
        "goal_topic": goal_topic,
        "preferences": {
            "preferred_type": preferred_type,
            "difficulty": difficulty,
            "max_length": max_length
        }
    }

    with st.spinner("✨ Crafting your personalized journey..."):
        try:
            response = requests.post("http://127.0.0.1:5000/api/get-learning-path", json=payload)
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Learning Path Generated")

                for idx, item in enumerate(data["learning_path"], start=1):
                    st.markdown(f"## Step {idx}: {item['topic']}")

                    cols = st.columns(2)
                    resources = item["recommended_resources"]

                    if resources:
                        for i, res in enumerate(resources):
                            with cols[i % 2]:
                                thumbnail = res.get("thumbnail") or get_youtube_thumbnail(res["url"])

                                st.markdown(
                                    f"""
                                    <div class="card">
                                        <img src="{thumbnail}" alt="Thumbnail">
                                        <h4>{res['title']}</h4>
                                        <div>
                                            <span class="tag">{preferred_type}</span>
                                            <span class="tag">{difficulty}</span>
                                            <span class="tag">{max_length} min</span>
                                        </div>
                                        <p><a href="{res['url']}" target="_blank">🔗 Open Resource</a></p>
                                    </div>
                                    """, unsafe_allow_html=True
                                )
                    else:
                        st.warning("⚠️ No resources found for this step.")

            else:
                st.error(f"❌ Error: {response.json().get('error', 'Unknown error')}")

        except Exception as e:
            st.error(f"❌ Request failed: {e}")

# ---------- Footer ----------
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with ❤️ by Kartik Bhargava and Lakshay Tomar</p>", unsafe_allow_html=True)
