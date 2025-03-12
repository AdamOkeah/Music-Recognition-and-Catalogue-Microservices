import sqlite3

DATABASE = 'shamzam.db'

def init_db():
    """Initializes the database and creates the tracks table (stores Base64 files)"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tracks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            artist TEXT NOT NULL,
                            file_data TEXT NOT NULL)''')  #  Store Base64 string
        conn.commit()

def add_track_to_db(title, artist, file_data):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tracks (title, artist, file_data) VALUES (?, ?, ?)",
                       (title, artist, file_data))  #  Store Base64 data
        conn.commit()
        return cursor.lastrowid  #  Return track ID

    

def get_all_tracks():
    """Retrieves all tracks stored in the database (Excludes encoded file)"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, artist FROM tracks")  #  No file_data in query
        tracks = cursor.fetchall()
    
    return [{"id": row[0], "title": row[1], "artist": row[2]} for row in tracks]  #  No file_data

def get_track_by_title_artist(title, artist):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, file_data FROM tracks WHERE title = ? AND artist = ?", 
                       (title, artist))
        track = cursor.fetchone()

    if track:
        file_data = track[1]

       
        if file_data.startswith("{"):
            print(f"Error: Stored file_data looks like JSON: {file_data[:50]}")
            return None

        print(f"🔹 Retrieved Base64 (first 50 chars): {file_data[:50]}") 
        return {
            "title": track[0],
            "file_data": file_data  #  Already Base64, do NOT decode it
        }
    
    return None  # Track not found

    



def remove_track_from_db(title, artist):
    """Removes a track from the database by its title and artist"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE title = ? and artist = ?", (title, artist))
        conn.commit()

        return cursor.rowcount > 0  #Returns True if deleted, False otherwise

def reset_db():
    """Clears the database and resets the ID counter"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tracks")  # Deletes the table

       
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='tracks'")  # Resets ID counter
        except sqlite3.OperationalError:
           
            pass

        conn.commit()
        init_db()  # Recreate the table

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
