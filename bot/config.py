from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
    token: str
    prefix: str
    log_level: str
    default_language: str
    data_dir: str



def load_config() -> Config:
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")

    return Config(
        token=token,
        prefix=os.getenv("COMMAND_PREFIX", "!"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        default_language=os.getenv("DEFAULT_LANGUAGE", "en"),
        data_dir=os.getenv("DATA_DIR", "data"),
    )
