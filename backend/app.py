import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from main import Manager

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
genAI = Manager()

def clean_response(text):
    # Remove Markdown bold (**bold** → bold)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)

    # Ensure proper spacing after punctuation
    text = re.sub(r'(?<=\w)\.(?=[A-Z])', '. ', text)

    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)

    # Add paragraph breaks before section headers
    text = re.sub(r'(?<=\n)([A-Z].*?:)', r'\n\n\1', text)  # Matches headers

    # Add paragraph breaks before bullet points or lists
    text = re.sub(r'(\n[-*])', r'\n\n\1', text)

    return text.strip()

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
    # print(data)
    prompt = data.get("prompt", "")
    # jsonString = data.get("jsonString", "{}")
    # history = json.loads(jsonString) if isinstance(jsonString, str) else jsonString
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    response_text = genAI.query(prompt).text
    return jsonify({"response": response_text.replace("\n", "<br>")})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
