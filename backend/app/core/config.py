from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "PLC Diagnostics Bridge"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = False
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Connection
    CONNECTION_TIMEOUT_SEC: int = 5
    MAX_CONNECTIONS: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
