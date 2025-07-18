from flask import Flask, jsonify, request
import networkx as nx

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

    if not known_topic or not goal_topic:
        return jsonify({"error": "Please provide both 'known_topic' and 'goal_topic'."}), 400

    try:
        path = nx.shortest_path(G, source=known_topic, target=goal_topic)
        return jsonify({"learning_path": path}), 200
    except nx.NetworkXNoPath:
        return jsonify({"error": f"No path found between {known_topic} and {goal_topic}."}), 404
    except nx.NodeNotFound as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(debug=True)
