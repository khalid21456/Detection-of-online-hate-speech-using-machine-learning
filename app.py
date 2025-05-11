from flask import Flask, request, jsonify, make_response
import torch
import json 
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification
app = Flask(__name__)

MODEL_PATH = "./model"


tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.eval()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    return response

@app.route('/detect', methods=['POST', 'OPTIONS'])
def detect_hate_speech():
    if request.method == 'OPTIONS':
        return make_response('', 200)

    data = request.get_json()
    text = data.get('text', '')
    print(f"Received: {text}")

    hate_phrases = ['i hate racist people']
    text_lower = text.lower()

    # Split text by commas and periods using regex, and strip whitespace
    parts = [part.strip() for part in re.split(r'[,.]', text_lower)]

    # Check if any of the parts match hate phrases
    detected_hate_speech = [phrase for phrase in hate_phrases if phrase in parts]

    print(f"Detected: {detected_hate_speech}")
    return jsonify({'detected_terms': detected_hate_speech})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Split the input text by commas and periods
    phrases = [p.strip() for p in re.split(r'[,.?!;]', text.lower()) if p.strip()]

    hate_phrases = []

    for phrase in phrases:
        # Tokenize and predict
        inputs = tokenizer(phrase, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=1).item()

        # If predicted as hate speech (assuming 1 means hate)
        if predicted_class == 0  or predicted_class == 1 :
            hate_phrases.append(phrase)

    return jsonify({"detected_terms": hate_phrases})

if __name__ == '__main__':
    app.run(debug=True)
