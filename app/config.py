import os
from dotenv import load_dotenv

DATABASE_PATH = os.path.join(os.getcwd(), 'shamzam.db')

# ✅ Ensure the environment file is loaded
env_path = os.path.join(os.path.dirname(__file__), 'api.env')
load_dotenv(env_path)

# ✅ Read the API token
AUDD_API_KEY = os.getenv('AUDD_API_KEY')

# ✅ Debugging: Print API key (only first 5 characters for security)
if not AUDD_API_KEY:
    print("❌ Error: AUDD_API_KEY is NOT set! Check your api.env file.")
else:
    print(f"✅ Loaded API Token: {AUDD_API_KEY[:5]}... (hidden for security)")

