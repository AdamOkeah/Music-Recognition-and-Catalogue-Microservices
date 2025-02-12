import sqlite3
from flask import jsonify

DATABASE = 'shamzam.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tracks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            artist TEXT NOT NULL,
                            file_path TEXT NOT NULL)''')
        conn.commit()

def reset_db():
    """Clears the database and resets the ID counter"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tracks")  # ✅ Deletes the tracks table
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tracks'")  # ✅ Resets ID counter
        conn.commit()
        init_db()  # ✅ Recreate the tracks table
        print("✅ Database has been reset!")

        

def add_track_to_db(title, artist, file_path):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tracks (title, artist, file_path) VALUES (?, ?, ?)", 
                       (title, artist, file_path))
        conn.commit()
    return jsonify({'message': 'Track added successfully'}), 201

def get_all_tracks():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, artist FROM tracks")
        tracks = cursor.fetchall()
    return jsonify([{'id': row[0], 'title': row[1], 'artist': row[2]} for row in tracks])

def remove_track_from_db(track_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({'error': 'Track not found'}), 404
    return jsonify({'message': 'Track removed successfully'}), 200
