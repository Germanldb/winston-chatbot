import httpx
from ..core.config import settings

class WhatsAppService:
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{settings.META_WHATSAPP_API_VERSION}/{settings.META_WHATSAPP_PHONE_NUMBER_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.META_WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

    async def send_text_message(self, to: str, text: str):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=self.headers, json=payload)
            return response.json()

    async def get_media_url(self, media_id: str):
        url = f"https://graph.facebook.com/{settings.META_WHATSAPP_API_VERSION}/{media_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            media_data = response.json()
            actual_url = media_data.get("url")
            
            # Now we need to download/get the source using the token again
            if actual_url:
                return actual_url
        return None

whatsapp_service = WhatsAppService()
