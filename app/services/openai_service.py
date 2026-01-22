import openai
from ..core.config import settings
from .woocommerce_service import woocommerce_service

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_chat_response(self, customer_id: str, message: str, history: list = []):
        # We can inject product info here if needed
        messages = [
            {"role": "system", "content": "Eres un experto asesor de ventas de la tienda de zapatos Winston And Harry. Tu objetivo es ayudar a los clientes a encontrar el calzado perfecto. Sé amable, profesional y elegante. Si te preguntan por productos, intenta dar detalles sobre tallas y colores si los conoces. La tienda está en " + (settings.TIENDAS_URL or "nuestra web")},
        ]
        
        # Add history
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
            
        messages.append({"role": "user", "content": message})

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content

    async def analyze_image(self, image_url: str):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente visual para Winston And Harry. Identifica el modelo de zapato en la imagen. Intenta ser específico con el estilo y color."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "¿Qué producto es este? Dame solo el nombre probable del modelo para buscarlo en el inventario."},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url},
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content

openai_service = OpenAIService()
