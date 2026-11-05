import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_RAW_DIR = DATA_DIR / "raw"
UPLOAD_PROCESSED_DIR = DATA_DIR / "processed"
SAMPLE_DATA_DIR = DATA_DIR / "sample"

# Ensure directories exist
UPLOAD_RAW_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "DRISTHI"
    PROJECT_TAGLINE: str = "From ECG Signals to Timely Action"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dristhi_super_secure_secret_key_change_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/dristhi.db")
    
    # Paths
    UPLOAD_RAW_DIR: Path = UPLOAD_RAW_DIR
    UPLOAD_PROCESSED_DIR: Path = UPLOAD_PROCESSED_DIR
    SAMPLE_DATA_DIR: Path = SAMPLE_DATA_DIR

    # Upload limits
    MAX_FILE_SIZE_BYTES: int = 25 * 1024 * 1024  # 25 MB
    ALLOWED_EXTENSIONS: set = {".png", ".jpg", ".jpeg", ".xml", ".dcm", ".csv", ".dat", ".hea", ".json"}
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # AI & Research Mode
    RESEARCH_DEMO_ENABLED: bool = True
    MODEL_STATUS: str = "Awaiting Research-Backed Algorithm Selection"
    HARDWARE_STATUS: str = "Awaiting ESP32 / AD8232 Hardware Integration"

settings = Settings()
