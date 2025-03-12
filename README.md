# Shamzam

A microservices-based audio recognition system inspired by Shazam. This project integrates the [Audd.io](https://audd.io/) API for recognition and leverages SQLite to store tracks. Each microservice runs independently on a different port, handling a distinct portion of the workflow.

---


## Overview

**Shamzam** is designed to:  
- **Add** new tracks (title, artist, and file data) to a local SQLite database.  
- **List** the tracks, including basic information (ID, title, artist).  
- **Delete** specific tracks by title and artist.  
- **Recognize** an audio fragment by calling the Audd.io API, then searching for a match in the local database.

This microservices approach ensures that each component (e.g., adding tracks, listing tracks, recognizing audio) runs independently, improving scalability and maintainability.

---

## Database

This project uses a lightweight SQLite database named **shamzam.db**, which is automatically created if it does not exist. The table structure includes columns for track ID, title, artist, and file data (stored as Base64-encoded audio).

### Key Points
- No separate dataset file is used; instead, data is stored directly in SQLite.  
- Each microservice can initialize or modify the database when it starts.

---

## Key Features

1. **Microservices Architecture**  
   Each service (add, list, delete, recognize) is run separately, allowing modular development.

2. **Audio Storage as Base64**  
   Audio files are converted to Base64 strings and stored in the database for easy retrieval.

3. **Integration with Audd.io**  
   Audio recognition is powered by the Audd.io API, requiring an `AUDD_KEY` environment variable.

4. **RESTful Endpoints**  
   Each microservice exposes a clean and simple REST API, making interaction straightforward.

5. **SQLite for Simplicity**  
   A file-based database is used to keep setup easy. No separate server or complex configuration is required.

---

## Microservice Architecture

- **Add Track Service**  
  Responsible for reading an audio file, encoding it, and inserting the record into the database.  
- **List Tracks Service**  
  Retrieves track information (ID, title, artist) from the database without exposing audio file data.  
- **Delete Track Service**  
  Deletes entries from the database using title and artist as identifiers.  
- **Recognition Service**  
  Sends audio fragments to Audd.io, obtains recognized title/artist, and checks if a matching record exists in the local database.

Each service uses Flask and runs on its own port (e.g., 5000 for adding, 5001 for listing, 5002 for deleting, 5003 for recognition).

---

## Usage

### Prerequisites
- **Python 3.7+**  
- **Flask**, **requests**, and optionally **python-dotenv** if loading environment variables from a file  
- **Audd.io API key**, set as an environment variable:
  ```bash
  export AUDD_KEY='your_audd_key_here'
