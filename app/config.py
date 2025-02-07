import os
from dotenv import load_dotenv

DATABASE_PATH = os.path.join(os.getcwd(), 'shamzam.db')
AUDD_API_KEY = os.getenv('AUDD_API_KEY')  # Load from environment variable
