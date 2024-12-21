from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sns_topic_arn: str = "arn:aws:sns:region:123456789012:test-topic"


@lru_cache
def get_settings() -> Settings:
    return Settings()
