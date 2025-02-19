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
                            file_data TEXT NOT NULL)''')  # ✅ Still stores Base64 files
        conn.commit()

def add_track_to_db(title, artist, file_path):
    """Adds a track entry to the database with Base64-encoded file"""
    try:
        # ✅ Read and encode the WAV file in Base64
        with open(file_path, "rb") as file:
            encoded_file = base64.b64encode(file.read()).decode('utf-8')  # ✅ Convert to Base64 string

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tracks (title, artist, file_data) VALUES (?, ?, ?)",
                           (title, artist, encoded_file))  # ✅ Store Base64 data
            conn.commit()
        print(f"Stored track in database: {title} - {artist} (File stored as Base64)")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")

def get_all_tracks():
    """Retrieves all tracks stored in the database (Excludes encoded file)"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, artist FROM tracks")  # ✅ No file_data
        tracks = cursor.fetchall()
    
    return [{"id": row[0], "title": row[1], "artist": row[2]} for row in tracks]  # ✅ No file_data

def get_track_by_title(title):
    """Retrieves a track by title (returns metadata but not file)"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, artist FROM tracks WHERE title = ?", (title,))
        track = cursor.fetchone()

    if track:
        return {"title": track[0], "artist": track[1]}  # ✅ No file_data
    
    return None

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
