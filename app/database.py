import sqlite3
import base64

DATABASE = 'shamzam.db'

def init_db():
    """Initializes the database and creates the tracks table (stores Base64 files)"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tracks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            artist TEXT NOT NULL,
                            file_data TEXT NOT NULL)''')  # ✅ Store encrypted Base64 file
        conn.commit()

def add_track_to_db(title, artist, file_data):
    """Adds a track entry to the database with an encrypted Base64-encoded file"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tracks (title, artist, file_data) VALUES (?, ?, ?)",
                       (title, artist, file_data))  # ✅ Store Base64 data
        conn.commit()
        return cursor.lastrowid  # Return track ID

def get_all_tracks():
    """Retrieves all tracks stored in the database (Excludes encoded file)"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, artist FROM tracks")  # ✅ No file_data in query
        tracks = cursor.fetchall()
    
    return [{"id": row[0], "title": row[1], "artist": row[2]} for row in tracks]  # ✅ No file_data

def get_track_by_title_artist(title, artist):
    """Retrieves a track from the database, including Base64 file data"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, file_data FROM tracks WHERE title = ? AND artist = ?", 
                       (title, artist))
        track = cursor.fetchone()

    if track:
        return {
            "title": track[0],
            "file_data": track[1]  # ✅ Return Base64-encoded file as-is
        }
    
    return None  # Track not found

    


def remove_track_from_db(track_id):
    """Removes a track from the database by its ID"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Track with ID {track_id} removed successfully.")
            return True
        else:
            print(f"No track found with ID {track_id}.")
            return False

def reset_db():
    """Clears the database and resets the ID counter"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tracks")  # Deletes the table
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tracks'")  # Resets ID counter
        conn.commit()
        init_db()  # Recreate the table
        print("Database has been reset.")
