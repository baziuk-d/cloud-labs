from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    POSTGRES_USER: str = "sensor_user"
    POSTGRES_PASSWORD: str = "sensor_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sensor_emulator"
    
    # Application settings
    TARGET_URL: str = "http://localhost:8000/api/emulator/data/receive"
    
    GCP_PROJECT_ID: str = ""
    GCP_CREDENTIALS_PATH: str = "./gcp-credentials.json"
    
    # Pub/Sub Topics for different sensor types
    GCP_TOPIC_TEMPERATURE: str = "sensor-temperature"
    GCP_TOPIC_HUMIDITY: str = "sensor-humidity"
    GCP_TOPIC_LIGHT: str = "sensor-light"
    
    # Subscriptions
    GCP_SUBSCRIPTION_TEMPERATURE: str = "sensor-temperature-sub"
    GCP_SUBSCRIPTION_HUMIDITY: str = "sensor-humidity-sub"
    GCP_SUBSCRIPTION_LIGHT: str = "sensor-light-sub"
    
    # Cloud Functions URLs (отримаєте після deployment)
    CLOUD_FUNCTION_HISTORY_URL: str = ""  # Буде виглядати як: https://REGION-PROJECT_ID.cloudfunctions.net/get-sensor-history
    CLOUD_FUNCTION_REGION: str = "us-central1"

    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def sync_database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


def get_settings():
    return Settings()


settings = Settings()