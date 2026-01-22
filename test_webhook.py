import httpx
import asyncio
import json

async def test_webhook():
    url = "http://127.0.0.1:8000/api/v1/chat/webhook"
    
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "12345",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {"display_phone_number": "123", "phone_number_id": "456"},
                            "contacts": [{"profile": {"name": "Test User"}, "wa_id": "584245594122"}],
                            "messages": [
                                {
                                    "from": "584245594122",
                                    "id": "msg_123",
                                    "timestamp": "1625097600",
                                    "text": {"body": "Hola, ¿qué precios tienen los zapatos?"},
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

    print(f"Enviando mensaje de prueba a {url}...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            print(f"Respuesta del servidor: {response.status_code}")
            print(f"Cuerpo: {response.text}")
        except Exception as e:
            print(f"Error conectando con el servidor local: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook())
