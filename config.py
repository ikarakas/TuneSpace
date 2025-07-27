import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///tunespace.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    HF_TOKEN = os.getenv('HF_TOKEN')
    HF_CACHE_DIR = os.getenv('HF_CACHE_DIR', './cache')
    
    WANDB_API_KEY = os.getenv('WANDB_API_KEY')
    WANDB_PROJECT = os.getenv('WANDB_PROJECT', 'tunespace')
    
    DEFAULT_OUTPUT_DIR = os.getenv('DEFAULT_OUTPUT_DIR', './models')
    MAX_CONCURRENT_JOBS = int(os.getenv('MAX_CONCURRENT_JOBS', '2'))
    AUTO_CLEANUP_DAYS = int(os.getenv('AUTO_CLEANUP_DAYS', '30'))
    
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000').split(',')
    
    DATA_DIR = 'data'
    LOGS_DIR = 'logs'
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.DEFAULT_OUTPUT_DIR,
            cls.HF_CACHE_DIR,
            cls.DATA_DIR,
            cls.LOGS_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

config = Config()