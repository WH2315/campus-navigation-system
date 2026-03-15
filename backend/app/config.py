from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Campus AIGC Virtual Tour API"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Chat channel (preferred). If empty, fallback to OPENAI_*.
    chat_api_key: str = ""
    chat_base_url: str = ""
    chat_model: str = ""

    # ASR channel (preferred). If empty, fallback to OPENAI_*.
    asr_api_key: str = ""
    asr_base_url: str = ""
    asr_model: str = ""

    tts_engine: str = "mock"
    asr_engine: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
