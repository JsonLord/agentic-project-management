from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    JULES_PROFILE: str = "default_profile"
    DASHBOARD_URL: str = "https://harvesthealth-deepsite-project-4mnq5.hf.space"
    PLANDEX_URL: str = "https://auxteam-plandex.hf.space"
    CODING_CLI_URL: str = "https://harvesthealth-chat-app.hf.space"
    # Legacy JULES_API_URL removed

    class Config:
        env_file = ".env"

settings = Settings()
