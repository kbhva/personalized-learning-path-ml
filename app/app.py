import pandas as pd
import joblib
import networkx as nx
from flask import Flask, jsonify, request

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
    G.add_node(topic)

prerequisites = [
    ("Introduction to Python", "Data Structures"),
    ("Data Structures", "OOP Concepts"),
    ("OOP Concepts", "Introduction to ML"),
    ("Introduction to ML", "Linear Regression"),
    ("Introduction to ML", "Decision Trees"),
    ("Introduction to ML", "Neural Networks")
]

G.add_edges_from(prerequisites)

ranker_model = joblib.load('../models/resource_ranker.pkl')
resources_df = pd.read_csv('../datasets/resources.csv')

difficulty_map = {'easy': 1, 'medium': 2, 'hard': 3}
resources_df['difficulty_encoded'] = resources_df['difficulty'].map(difficulty_map)

type_map = {'video': 0, 'article': 1}
resources_df['type_encoded'] = resources_df['type'].map(type_map)

@app.route("/")
def home():
    return "Personalized Learning Path API is running."

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "OK", "message": "API is healthy"}), 200

@app.route("/api/get-learning-path", methods=["POST"])
def get_learning_path():
    data = request.get_json()
    known_topic = data.get("known_topic")
    goal_topic = data.get("goal_topic")
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
            topic_resources = resources_df[resources_df['topic'].str.strip() == topic.strip()]

            if preferred_type != "any":
                topic_resources = topic_resources[topic_resources['type_encoded'] == type_map_inv[preferred_type]]
            if difficulty != "any":
                topic_resources = topic_resources[topic_resources['difficulty_encoded'] == difficulty_map_inv[difficulty]]
            if max_length:
                topic_resources = topic_resources[topic_resources['length'] <= int(max_length)]

            if topic_resources.empty:
                response.append({
                    "topic": topic,
                    "recommended_resources": []
                })
                continue

            X_topic = topic_resources[['length', 'difficulty_encoded', 'type_encoded', 'popularity', 'rating']]
            topic_resources = topic_resources.copy()
            topic_resources['predicted_score'] = ranker_model.predict(X_topic)
            top_resources = topic_resources.sort_values(by='predicted_score', ascending=False).head(3)
            recommended = top_resources[['title', 'url', 'predicted_score']].to_dict(orient='records')

            response.append({
                "topic": topic,
                "recommended_resources": recommended
            })

        return jsonify({"learning_path": response}), 200

    except nx.NetworkXNoPath:
        return jsonify({"error": f"No path found between {known_topic} and {goal_topic}."}), 404
    except nx.NodeNotFound as e:
        return jsonify({"error": str(e)}), 404


if __name__ == "__main__":
    app.run(debug=True)
