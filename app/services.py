import requests
from flask import jsonify
import os
from app.config import AUDD_API_KEY

AUDD_API_KEY = os.getenv('AUDD_API_KEY')  # Load API key from environment variables

def recognise_audio(file):
    """Sends an audio fragment to AudD.io for recognition"""
    
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    
    try:
        # Send request to AudD.io API
        response = requests.post(
            'https://api.audd.io/',
            files={'file': file},
            data={'api_token': AUDD_API_KEY}
        )

        # Check if request was successful
        if response.status_code == 200:
            result = response.json()

            # If a song is found
            if result.get('result'):
                return jsonify({
                    'track': result['result']['title'],
                    'artist': result['result']['artist']
                }), 200
            else:
                return jsonify({'error': 'No match found'}), 404

    except Exception as e:
        return jsonify({'error': f'Failed to process audio: {str(e)}'}), 500


