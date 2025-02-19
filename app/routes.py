from flask import Blueprint, request, jsonify
import base64
from app.database import add_track_to_db, remove_track_from_db, get_all_tracks, get_track_by_title_artist
from app.services import recognise_audio

routes = Blueprint('routes', __name__)

@routes.route('/tracks', methods=['POST'])
def add_track():
    """Handles adding a track to the database (stores encrypted Base64 file)"""
    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400  # ✅ Requires actual file

    file = request.files['file']
    title = request.form.get("title")
    artist = request.form.get("artist")

    if not title or not artist:
        return jsonify({"error": "Missing title or artist"}), 400

    # ✅ Read and encode the WAV file in Base64
    encoded_file = base64.b64encode(file.read()).decode('utf-8')

    # ✅ Store in database
    track_id = add_track_to_db(title, artist, encoded_file)

    return jsonify({
        "message": "Track added successfully",
        "track": {
            "id": track_id,
            "title": title,
            "artist": artist
        }
    }), 201



@routes.route('/tracks', methods=['GET'])
def list_tracks():
    return get_all_tracks()

@routes.route('/tracks/<int:track_id>', methods=['DELETE'])
def remove_track(track_id):
    return remove_track_from_db(track_id)



@routes.route('/recognise', methods=['POST'])
def recognise_track():
    """Handles audio recognition requests and returns only title + encrypted file"""
    file = request.files.get('file')

    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    # ✅ Step 1: Recognise the fragment
    recognition_result, status_code = recognise_audio(file)
    if status_code != 200:
        return recognition_result, status_code  # Forward error response

    song_metadata = recognition_result.json  # Convert response to dictionary
    title = song_metadata.get("title")
    artist = song_metadata.get("artist")  # ✅ Needed for DB lookup, but not returned

    # ✅ Step 2: Check if the track is in the database
    stored_track = get_track_by_title_artist(title, artist)

    if stored_track:
        # ✅ Do NOT decode Base64 (return as-is)
        return jsonify({
            "message": "Track found in database",
            "track": {
                "title": stored_track["title"],
                "file_data": stored_track["file_data"]  # ✅ Send Base64 directly
            }
        }), 200

    return jsonify({
        "message": "Track not found in database",
        "metadata": song_metadata,
        "next_step": "Send a POST request to /tracks with this data to add it."
    }), 404