import streamlit as st
import requests

st.set_page_config(
    page_title="Personalized Learning Path",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Roboto:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; background-color: #f9fafb; }
    h1, h2, h3, h4 { font-family: 'Montserrat', sans-serif; color: #0f766e; }
    .stButton button {
        background-color: #0f766e;
        color: white;
        border: None;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-weight: 600;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover { background-color: #155e57; }
    .stMarkdown a { color: #0f766e; text-decoration: none; font-weight: 500; }
    .stMarkdown a:hover { text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>📚 Personalized Learning Path Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Build your AI-ranked, personalized learning journey.</p>", unsafe_allow_html=True)
st.write("---")

# Ordered topics
topics_order = [
    "Introduction to Python", "Data Structures", "OOP Concepts",
    "Introduction to ML", "Linear Regression", "Decision Trees", "Neural Networks"
]

known_topic = st.selectbox("✅ Your known topic:", topics_order)

# Filter goal topics to only those after the known topic
known_idx = topics_order.index(known_topic)
available_goal_topics = topics_order[known_idx:]  # topics from known_topic onwards

goal_topic = st.selectbox("🎯 Your goal topic:", available_goal_topics)

preferred_type = st.radio(
    "🎬 Preferred content type:",
    ["any", "video", "article"], horizontal=True
)

difficulty = st.radio(
    "🧩 Preferred difficulty:",
    ["any", "easy", "medium", "hard"], horizontal=True
)

max_length = st.slider("⏱️ Max content length (minutes):", 5, 180, 45)
st.write("---")

if st.button("🚀 Generate Learning Path"):
    payload = {
        "known_topic": known_topic,
        "goal_topic": goal_topic,
        "preferences": {
            "preferred_type": preferred_type,
            "difficulty": difficulty,
            "max_length": max_length
        }
    }

    with st.spinner("Generating your personalized learning path..."):
        try:
            response = requests.post("http://127.0.0.1:5000/api/get-learning-path", json=payload)
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Learning Path Generated")

                for idx, item in enumerate(data["learning_path"], start=1):
                    with st.expander(f"📖 {idx}. {item['topic']}"):
                        resources = item["recommended_resources"]
                        if resources:
                            for res in resources:
                                st.markdown(
                                    f"- [{res['title']}]({res['url']})"
                                )
                        else:
                            st.warning("⚠️ No resources found with these preferences.")
            else:
                st.error(f"❌ Error: {response.json().get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Request failed: {e}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made with ❤️ by Kartik Bhargava.</p>", unsafe_allow_html=True)
