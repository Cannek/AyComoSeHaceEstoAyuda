from dotenv import load_dotenv
import os
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ ERROR: Missing OPENAI_API_KEY in .env file!")

from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import sys
sys.path.append('./')  # Ensures Python looks in the current directory

from openai_chat import OpenAiManager, AICharacter, personajes  # Import AICharacter and your list of characters

app = Flask(__name__)
CORS(app)

# List of possible policies (in Spanish)
politicas = [
    "Aumentar los impuestos a los ricos",
    "Implementar salud pública universal"
    # Add more policies as needed...
]

@app.route('/generate_simulation', methods=['POST'])
def generate_simulation():
    """Receives party percentages and generates AI opinions and votes using AI characters."""
    data = request.json
    percentages = data.get("percentages", [])
    if sum(percentages) != 100:
        return jsonify({"error": "Los porcentajes deben sumar 100"}), 400

    # Choose a random policy
    politica = random.choice(politicas)

    selected_characters = []
    total_squares = 500  # Total number of squares
    grid_colors = []
    grid_votes = []

    # For each party percentage, if > 0, use the corresponding character from 'personajes'
    for i, percent in enumerate(percentages):
        num_squares = round(total_squares * (percent / 100))
        if num_squares > 0:
            # Use the character for this party (assume same order as percentages)
            personaje = personajes[i]
            personaje.generar_opiniones(politica)
            personaje.decidir_voto(politica)
            selected_characters.append(personaje)
            grid_colors.extend([personajes[i].creencias.get("Color", personaje.nombre)] * num_squares)  # fallback: you can adjust to use party color
            grid_votes.extend([{"color": personajes[i].creencias.get("Color", "#000000"), "decision": personaje.voto}] * num_squares)

    # Fill grid if less than 500 squares
    while len(grid_colors) < total_squares:
        grid_colors.append("#FFFFFF")
        grid_votes.append({"color": "#FFFFFF", "decision": ""})

    # Gather messages: get at least 2 opinions per selected character
    messages = []
    for personaje in selected_characters:
        # Get the first two opinions (or any selection method)
        for opiniones in personaje.opiniones[:2]:
            messages.append({
                "party": personaje.nombre,
                "color": personajes[selected_characters.index(personaje)].creencias.get("Color", "#000000"),
                "message": opiniones
            })
    random.shuffle(messages)  # For a realistic mix

    # Calculate overall success: if at least half the parties vote approval
    num_agree = sum(1 for p in selected_characters if p.voto == "✅")
    passed = num_agree >= (len(selected_characters) / 2)

    return jsonify({
        "politica": politica,
        "grid_colors": grid_colors,
        "grid_votes": grid_votes,
        "messages": messages,
        "final_results": [
            {"party": p.nombre, "decision": p.voto, "color": p.creencias.get("Color", "#000000")}
            for p in selected_characters
        ],
        "success": passed
    })

if __name__ == '__main__':
    app.run(debug=True)
