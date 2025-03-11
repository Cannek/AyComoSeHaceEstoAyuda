from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import sys
sys.path.append('./')  # Ensures Python looks in the current directory

from openai_chat import OpenAiManager  # Import from Babagaboosh

app = Flask(__name__)
CORS(app)
openai_manager = OpenAiManager()  # Initialize AI model

# Character definitions
characters = [
    {"name": "Red Party", "color": "#D9534F"},
    {"name": "Blue Party", "color": "#5BC0DE"},
    {"name": "Green Party", "color": "#5CB85C"},
    {"name": "Yellow Party", "color": "#F0AD4E"},
    {"name": "Purple Party", "color": "#9370DB"},
    {"name": "Orange Party", "color": "#FF8C00"},
    {"name": "Brown Party", "color": "#8B4513"},
    {"name": "Gray Party", "color": "#A9A9A9"}
]

# List of possible topics
topics = [
    "Increase taxes for the wealthy",
    "Implement universal healthcare",
    "Ban single-use plastics",
    "Increase funding for space exploration",
    "Legalize recreational marijuana",
    "Increase minimum wage",
    "Introduce mandatory military service",
    "Implement stricter gun control laws"
]

@app.route('/generate_simulation', methods=['POST'])
def generate_simulation():
    """Receives party percentages and generates AI opinions"""
    data = request.json
    percentages = data.get("percentages", [])  

    if sum(percentages) != 100:
        return jsonify({"error": "Percentages must add up to 100"}), 400

    topic = random.choice(topics)

    selected_characters = []
    total_squares = 500  # Number of squares in the grid
    grid_colors = []
    grid_votes = []
    messages = []

    # Assign squares based on party percentages
    for i, percent in enumerate(percentages):
        num_squares = round(total_squares * (percent / 100))
        
        if num_squares > 0:
            decision = random.choice(["✅", "❌"])  # Party votes together
            selected_characters.append({
                "party": characters[i]["name"],
                "color": characters[i]["color"],
                "num_members": num_squares,
                "opinions": [],
                "final_decision": decision  # Whole party votes the same way
            })
            grid_colors.extend([characters[i]["color"]] * num_squares)
            grid_votes.extend([{"color": characters[i]["color"], "decision": decision}] * num_squares)

    # Ensure exactly 500 squares (fill empty spots with white for neutral)
    while len(grid_colors) < total_squares:
        grid_colors.append("#FFFFFF")  # Neutral space
        grid_votes.append({"color": "#FFFFFF", "decision": ""})

    # Ensure each participating party contributes at least 2 messages
    for char in selected_characters:
        for _ in range(2):  # Each party must provide at least 2 opinions
            opinion = openai_manager.chat(prompt=f"The {char['party']} is debating the topic: {topic}. What is their position?")
            messages.append({
                "party": char["party"],
                "color": char["color"],
                "message": opinion
            })

    # Calculate overall success
    num_agree = sum(1 for char in selected_characters if char["final_decision"] == "✅")
    passed = num_agree >= (len(selected_characters) / 2)

    return jsonify({
        "topic": topic,
        "grid_colors": grid_colors,
        "grid_votes": grid_votes,  # Now all members of a party vote the same
        "messages": messages,
        "final_results": [
            {"party": char["party"], "decision": char["final_decision"], "color": char["color"]}
            for char in selected_characters
        ],
        "success": passed
    })

if __name__ == '__main__':
    app.run(debug=True)
