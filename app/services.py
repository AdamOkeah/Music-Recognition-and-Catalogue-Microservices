import requests
from flask import jsonify
import os
from app.config import AUDD_API_KEY

# ✅ Ensure API key is loaded
if not AUDD_API_KEY:
    print("❌ Error: AUDD_API_KEY is NOT set! Check your api.env file.")

def recognise_audio(file):
    """Sends an audio fragment to AudD.io for recognition."""
    
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        print(f"✅ Received file: {file.filename}")  # Debugging print
        print(f"✅ File type: {file.content_type}")  # Debugging print
        print(f"✅ Using API Token: {AUDD_API_KEY[:5]}... (hidden for security)")  # Debugging print

        # ✅ Send request to AudD.io API
        response = requests.post(
            'https://api.audd.io/',
            files={'file': (file.filename, file.stream, 'audio/wav')},  # ✅ Properly format file upload
            data={'api_token': AUDD_API_KEY}
        )

        print(f"✅ API Response Code: {response.status_code}")  # Debugging print
        print(f"✅ API Raw Response: {response.text}")  # Debugging print

        # ✅ Handle API response
        if response.status_code == 200:
            result = response.json()

            # ✅ If a song is found, return all metadata
            if 'result' in result and result['result']:
                return jsonify(result['result']), 200

            return jsonify({'error': 'No match found'}), 404  # No match found

        # ✅ Handle API authentication issues
        elif response.status_code == 403:
            return jsonify({'error': 'Unauthorized: Invalid API Token'}), 403

        return jsonify({'error': f'AudD.io Error: {response.status_code}'}), response.status_code

    except Exception as e:
        print(f"❌ Exception: {str(e)}")  # Debugging print
        return jsonify({'error': f'Failed to process audio: {str(e)}'}), 500
