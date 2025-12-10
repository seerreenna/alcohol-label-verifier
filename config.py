import os
from dotenv import load_dotenv # reads env files

if os.path.exists('.env'):
    load_dotenv()

class Config:
    """Base configuration for secret key"""
    SECRET_KEY = os.environ.get('SECRET_KEY') 

    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # around 16 MB 

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'} # common extension types for uploaded docs

    TESSERACT_CMD = os.environ.get('TESSERACT_CMD') or None

    # thresholds for validation
    SIMILARITY_THRESHOLD = 0.85  # 85% similarity for fuzzy matching
    ABV_TOLERANCE = 0.3  # Allows for 0.3% difference in alcohol content