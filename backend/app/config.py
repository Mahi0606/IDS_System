"""Configuration settings for the IDS backend."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "IDS System"
    VERSION: str = "1.0.0"
    
    # Network Interface
    # Common options: bridge0, bridge100, en0, enp0s1
    # - bridge0/bridge100: Multipass VMs on macOS
    # - en0: Primary network interface (macOS)
    # - enp0s1: Common Linux network interface
    INTERFACE_NAME: str = "bridge100"  # Default for macOS Multipass
    
    # Model Paths
    MODEL_DIR: str = "saved_models"
    BINARY_MODEL_PATH: str = "saved_models/binary_svm_model.pkl"
    MULTICLASS_MODEL_PATH: str = "saved_models/multiclass_rf_model.pkl"
    SCALER_PATH: str = "saved_models/scaler.pkl"
    PCA_PATH: str = "saved_models/pca.pkl"
    
    # Flow Manager Settings
    FLOW_IDLE_TIMEOUT: int = 60  # seconds
    FLOW_BATCH_SIZE: int = 10  # batch predictions
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

