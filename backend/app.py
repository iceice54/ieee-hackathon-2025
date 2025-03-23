from flask import Flask, request, jsonify
from flask_cors import CORS
from manager import Manager

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
genAI = Manager()

@app.after_request
def add_no_cache_headers(response):
    """Ensure responses are never cached."""
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/prompt", methods=["POST"])
def handle_prompt():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    response_text = genAI.query(prompt)
    if len(response_text) == 1:
        return jsonify({"response": response_text[0].text})
    else:
        return jsonify({"response": response_text[0].text + "\n" + response_text[1].text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
