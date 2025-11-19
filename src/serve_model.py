"""
Flask API of the SMS Spam detection model model.
"""
import joblib
import os
import urllib.request
from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import tarfile

from text_preprocessing import prepare, _extract_message_len, _text_process

app = Flask(__name__)
swagger = Swagger(app)

# Configuration from the environment variables
MODEL_DIR = os.getenv('MODEL_DIR', '/models')
MODEL_VERSION = os.getenv('MODEL_VERSION', 'latest')
MODEL_REPO = os.getenv('MODEL_REPO', 'doda25-team13/model-service')

def download_model_if_needed():
    """Download model from GitHub releases if not present locally."""
    model_path = os.path.join(MODEL_DIR, 'model.joblib')
    preprocessor_path = os.path.join(MODEL_DIR, 'preprocessor.joblib')

    # Check if models already exist and  Create dir if it doesn't exist
    if os.path.exists(model_path) and os.path.exists(preprocessor_path):
        print(f"Models found in {MODEL_DIR}")
        return

    os.makedirs(MODEL_DIR, exist_ok=True)


    if MODEL_VERSION == 'latest':
        api_url = f'https://api.github.com/repos/{MODEL_REPO}/releases/latest'
        import json
        with urllib.request.urlopen(api_url) as response:
            release_data = json.loads(response.read())
            download_url = release_data['assets'][0]['browser_download_url']
    else:
        download_url = f'https://github.com/{MODEL_REPO}/releases/download/v{MODEL_VERSION}/model-v{MODEL_VERSION}.tar.gz'

    print(f"Downloading model from {download_url}")


    tar_path = os.path.join(MODEL_DIR, 'model.tar.gz')
    urllib.request.urlretrieve(download_url, tar_path)


    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(MODEL_DIR)

    os.remove(tar_path)
    print(f"Model extracted to {MODEL_DIR}")


download_model_if_needed()
model = joblib.load(os.path.join(MODEL_DIR, 'model.joblib'))


@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict whether an SMS is Spam.
    ---
    consumes:
      - application/json
    parameters:
        - name: input_data
          in: body
          description: message to be classified.
          required: True
          schema:
            type: object
            required: sms
            properties:
                sms:
                    type: string
                    example: This is an example of an SMS.
    responses:
      200:
        description: "The result of the classification: 'spam' or 'ham'."
    """
    input_data = request.get_json()
    sms = input_data.get('sms')
    processed_sms = prepare(sms)
    #model = joblib.load('output/model.joblib')
    prediction = model.predict(processed_sms)[0]
    
    res = {
        "result": prediction,
        "classifier": "decision tree",
        "sms": sms
    }
    print(res)
    return jsonify(res)

if __name__ == '__main__':
    #clf = joblib.load('output/model.joblib')
    port = int(os.getenv("MODEL_SERVICE_PORT", "8081"))
    app.run(host="0.0.0.0", port=port, debug=True)
