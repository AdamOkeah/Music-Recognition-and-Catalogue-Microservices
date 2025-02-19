from flask import Blueprint, request, jsonify
from app.database import add_track_to_db, remove_track_from_db, get_all_tracks
from app.services import recognise_audio

routes = Blueprint('routes', __name__)

@routes.route('/tracks', methods=['POST'])
def add_track():
    """Handles adding a track to the database (including file path)"""
    data = request.get_json()

    if not data or "title" not in data or "artist" not in data or "file_path" not in data:
        return jsonify({"error": "Missing fields"}), 400  # ✅ Now requires "file_path"

    title = data["title"]
    artist = data["artist"]
    file_path = data["file_path"]

    # ✅ Store in database
    add_track_to_db(title, artist, file_path)

    return jsonify({"message": "Track added successfully"}), 201


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