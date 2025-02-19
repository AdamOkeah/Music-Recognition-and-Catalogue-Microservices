import requests
from flask import jsonify
import os
from app.config import AUDD_API_KEY

if not AUDD_API_KEY:
    print("❌ Error: AUDD_API_KEY is NOT set! Check your api.env file.")

def recognise_audio(file):
    """Sends an audio fragment to AudD.io for recognition."""
    
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        response = requests.post(
            'https://api.audd.io/',
            files={'file': (file.filename, file.stream, 'audio/wav')},
            data={'api_token': AUDD_API_KEY}
        )

        print(f"✅ API Response Code: {response.status_code}")  
        print(f"✅ API Raw Response: {response.json()}")  # Print full API response

        if response.status_code == 200:
            result = response.json()

            if 'result' in result and result['result']:
                song_data = result['result']

                # ✅ Ensure album is extracted correctly
                return jsonify(song_data), 200  # Return the full response

            return jsonify({'error': 'No match found'}), 404  

        return jsonify({'error': f'AudD.io Error: {response.status_code}'}), response.status_code

    except Exception as e:
        return jsonify({'error': f'Failed to process audio: {str(e)}'}), 500
