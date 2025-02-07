from flask import Blueprint, request, jsonify
from app.database import add_track_to_db, remove_track_from_db, get_all_tracks
from app.services import recognise_audio

routes = Blueprint('routes', __name__)

@routes.route('/tracks', methods=['POST'])
def add_track():
    print("Received POST request to /tracks")  # Debug log

    data = request.json
    if not data:
        print("No data received!")  # Debug log
        return jsonify({'error': 'No data received'}), 400

    title, artist, file = data.get('title'), data.get('artist'), data.get('file')

    if not title or not artist or not file:
        print("Missing fields!")  # Debug log
        return jsonify({'error': 'Missing fields'}), 400

    print(f"✅ Adding track: {title} by {artist}")  # Debug log
    return add_track_to_db(title, artist, file)


@routes.route('/tracks', methods=['GET'])
def list_tracks():
    return get_all_tracks()

@routes.route('/tracks/<int:track_id>', methods=['DELETE'])
def remove_track(track_id):
    return remove_track_from_db(track_id)



@routes.route('/recognise', methods=['POST'])
def recognise_track():
    """Handles audio recognition requests"""
    file = request.files.get('file')
    return recognise_audio(file)