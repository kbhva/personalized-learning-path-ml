import os
import pandas as pd
import joblib
import networkx as nx
from flask import Flask, jsonify, request
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

app = Flask(__name__)

G = nx.DiGraph()
topics = [
    "Introduction to Python",
    "Data Structures",
    "OOP Concepts",
    "Introduction to ML",
    "Linear Regression",
    "Decision Trees",
    "Neural Networks"
]
for topic in topics:
    G.add_node(topic.lower().strip())
prerequisites = [
    ("Introduction to Python", "Data Structures"),
    ("Data Structures", "OOP Concepts"),
    ("OOP Concepts", "Introduction to ML"),
    ("Introduction to ML", "Linear Regression"),
    ("Introduction to ML", "Decision Trees"),
    ("Introduction to ML", "Neural Networks")
]
G.add_edges_from((src.lower().strip(), tgt.lower().strip()) for src, tgt in prerequisites)

resources_path = '../datasets/resources_with_embeddings.csv'
resources_df = pd.read_csv(resources_path)
resources_df['topic'] = resources_df['topic'].str.strip().str.lower()
difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
resources_df['difficulty_encoded'] = resources_df['difficulty'].map(difficulty_map)
type_map = {'video': 0, 'article': 1}
resources_df['type_encoded'] = resources_df['type'].map(type_map)
ranker_path = '../models/resource_ranker.pkl'
if os.path.exists(ranker_path):
    ranker_model = joblib.load(ranker_path)
else:
    ranker_model = None

embed_model = SentenceTransformer("all-mpnet-base-v2")
resources_df['embedding_title'] = resources_df['embedding_title'].apply(lambda x: np.fromstring(x, sep=','))
resources_df['embedding_description'] = resources_df['embedding_description'].apply(lambda x: np.fromstring(x, sep=','))
title_embeddings = normalize(np.vstack(resources_df['embedding_title'].values))
desc_embeddings = normalize(np.vstack(resources_df['embedding_description'].values))

@app.route("/")
def home():
    return "Personalized Learning Path API is running."

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK", "message": "API is healthy"}), 200

@app.route("/api/get-learning-path", methods=["POST"])
def get_learning_path():
    data = request.get_json()
    known_topic = data.get("known_topic", "").strip().lower()
    goal_topic = data.get("goal_topic", "").strip().lower()
    preferences = data.get("preferences", {})

    if not known_topic or not goal_topic:
        return jsonify({"error": "Please provide both 'known_topic' and 'goal_topic'."}), 400

    preferred_type = preferences.get("preferred_type", "any")
    difficulty = preferences.get("difficulty", "any")
    max_length = preferences.get("max_length", None)

    type_map_inv = {"video": 0, "article": 1}
    difficulty_map_inv = {"easy": 1, "medium": 2, "hard": 3}

    try:
        path = nx.shortest_path(G, source=known_topic, target=goal_topic)
        response = []

        for topic in path:
            topic_resources = resources_df[resources_df['topic'] == topic]
            if preferred_type != "any":
                topic_resources = topic_resources[topic_resources['type_encoded'] == type_map_inv.get(preferred_type, -1)]
            if difficulty != "any":
                topic_resources = topic_resources[topic_resources['difficulty_encoded'] == difficulty_map_inv.get(difficulty, -1)]
            if max_length:
                topic_resources = topic_resources[topic_resources['length'] <= int(max_length)]
            if topic_resources.empty:
                response.append({"topic": topic.title(), "recommended_resources": []})
                continue

            query_text = f"Best learning resources for {topic}"
            topic_emb = embed_model.encode(query_text, show_progress_bar=False)
            topic_emb = topic_emb / np.linalg.norm(topic_emb)
            title_sim = title_embeddings.dot(topic_emb)
            desc_sim = desc_embeddings.dot(topic_emb)
            sim_score = 0.3 * title_sim + 0.7 * desc_sim


            topic_resources = topic_resources.copy()
            topic_resources['semantic_score'] = sim_score[topic_resources.index]

            if ranker_model is not None:
                X_topic = topic_resources[['length', 'difficulty_encoded', 'type_encoded', 'popularity', 'rating']]
                topic_resources['ml_score'] = ranker_model.predict(X_topic)
                alpha = 0.5
                topic_resources['final_score'] = alpha * topic_resources['ml_score'] + (1 - alpha) * topic_resources['semantic_score']
            else:
                topic_resources['final_score'] = topic_resources['semantic_score']

            topic_resources = topic_resources.sort_values(by='final_score', ascending=False).head(20)
            recommended = topic_resources[['title', 'url', 'final_score']].to_dict(orient='records')
            response.append({"topic": topic.title(), "recommended_resources": recommended})

        return jsonify({"learning_path": response}), 200

    except nx.NetworkXNoPath:
        return jsonify({"error": f"No path found between {known_topic} and {goal_topic}."}), 404
    except nx.NodeNotFound as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(debug=True)
