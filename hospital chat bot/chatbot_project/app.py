from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
import json
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.preprocessing import LabelEncoder
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load the pre-trained model
model = load_model('chatbot_model.h5')

# Load your illness data
with open('am_ill.json') as file:
    data = json.load(file)

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Prepare words and classes
words = []
classes = []

for illness in data['illnesses']:
    illness_name = illness['illness']
    for symptom in illness['symptoms']:
        words.append(lemmatizer.lemmatize(symptom.lower()))
        classes.append(illness_name)

# Remove duplicates and sort
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

# Function to preprocess user input
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bow_array = [0] * len(words)
    for word in sentence_words:
        if word in words:
            bow_array[words.index(word)] = 1
    return np.array(bow_array)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    symptoms_input = data.get('symptoms', [])

    if not symptoms_input:
        return jsonify({"error": "No symptoms provided"}), 400

    # Convert symptoms input to bag-of-words
    symptoms_text = ' '.join(symptoms_input)  # Join symptoms for processing
    bow_input = bow(symptoms_text, words)
    bow_input = np.array([bow_input])

    # Predict the illness
    prediction = model.predict(bow_input)
    predicted_class_index = np.argmax(prediction)
    confidence = prediction[0][predicted_class_index]

    # Confidence threshold (adjust as needed)
    confidence_threshold = 0.5

    if confidence < confidence_threshold:
        return jsonify({
            "message": "The model is not confident about the prediction. Please provide more symptoms for a better diagnosis."
        })

    predicted_illness = classes[predicted_class_index]

    # Create a response with the predicted illness and confidence
    return jsonify({
        "possible_illnesses": [{
            "illness": predicted_illness,
            "confidence": f"{confidence * 100:.2f}%"
        }]
    })



if __name__ == "__main__":
    app.run(debug=True)
