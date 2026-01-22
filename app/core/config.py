from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost/wh_chatbot"

    # OpenAI
    OPENAI_API_KEY: str

    # WooCommerce
    WOOCOMMERCE_URL: str
    WOOCOMMERCE_CONSUMER_KEY: str
    WOOCOMMERCE_CONSUMER_SECRET: str

    # Meta WhatsApp
    META_WHATSAPP_ACCESS_TOKEN: str
    META_WHATSAPP_PHONE_NUMBER_ID: str
    META_WHATSAPP_API_VERSION: str = "v24.0"
    META_WHATSAPP_VERIFY_TOKEN: str
    META_APP_ID: Optional[str] = None
    META_APP_SECRET: Optional[str] = None

    # URLs
    GUIA_TALLAS_URL: Optional[str] = None
    TIENDAS_URL: Optional[str] = None
    FAQ_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
