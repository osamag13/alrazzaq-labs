from flask import Flask, request, jsonify
import joblib

model = joblib.load('model.pkl')

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Simple API for Inference!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    prediction = model.predict([data['input']])
    return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(debug=True)
