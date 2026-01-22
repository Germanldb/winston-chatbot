from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database import get_db
from ...models.models import Customer, Message, BotStats
from ...services.openai_service import openai_service
from ...services.whatsapp_service import whatsapp_service
from ...services.woocommerce_service import woocommerce_service
from ...core.config import settings
import json

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.META_WHATSAPP_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    print(f"Recibido Webhook: {json.dumps(data, indent=2)}")
    
    # Meta envía notificaciones de estado (delivered, read, etc.) que no tienen el campo 'messages'
    try:
        if not data.get("entry") or not data["entry"][0].get("changes") or "messages" not in data["entry"][0]["changes"][0]["value"]:
            print("Webhook recibido pero no es un mensaje (posiblemente un cambio de estado).")
            return {"status": "ignored"}

        value = data["entry"][0]["changes"][0]["value"]
        msg = value["messages"][0]
        sender_id = msg["from"]
        msg_type = msg["type"]
        
        # Get or create customer
        customer = db.query(Customer).filter(Customer.whatsapp_id == sender_id).first()
        if not customer:
            contact_name = value.get("contacts", [{}])[0].get("profile", {}).get("name", "Cliente")
            customer = Customer(whatsapp_id=sender_id, name=contact_name)
            db.add(customer)
            db.commit()
            db.refresh(customer)
            print(f"Nuevo cliente creado: {contact_name} ({sender_id})")

        content = ""
        media_url = None

        if msg_type == "text":
            content = msg["text"]["body"]
        elif msg_type == "image":
            media_id = msg["image"].get("id")
            # En modo prueba, a veces el ID de imagen no es accesible directamente
            content = "[Imagen enviada]"
            print(f"Imagen recibida con ID: {media_id}")
            
            # En un entorno real, descargaríamos la imagen aquí. 
            # Como demostración, usaremos un texto descriptivo si no hay URL accesible.
            try:
                media_url = await whatsapp_service.get_media_url(media_id)
                if media_url:
                    product_guess = await openai_service.analyze_image(media_url)
                    content = f"Analizando producto: {product_guess}"
            except Exception as e:
                print(f"Error analizando imagen: {e}")
                content = "El cliente envió una imagen de un producto."

        print(f"Procesando mensaje de {sender_id}: {content}")

        # Guardar mensaje entrante
        db_msg = Message(
            customer_id=customer.id,
            direction="inbound",
            content=content,
            msg_type=msg_type,
            media_url=media_url
        )
        db.add(db_msg)
        
        # Estadísticas
        stats = BotStats(event_type="message_received", details={"type": msg_type, "customer_id": customer.id})
        db.add(stats)
        db.commit()

        # Generar respuesta con IA
        history = db.query(Message).filter(Message.customer_id == customer.id).order_by(Message.timestamp.desc()).limit(5).all()
        history_formatted = [{"role": "user" if m.direction == "inbound" else "assistant", "content": m.content} for m in reversed(history)]
        
        ai_response = await openai_service.get_chat_response(customer.id, content, history_formatted)
        print(f"Generada respuesta IA: {ai_response[:50]}...")
        
        # Enviar vía WhatsApp
        wa_response = await whatsapp_service.send_text_message(sender_id, ai_response)
        print(f"Respuesta enviada a WhatsApp: {wa_response.get('messaging_product')}")
        
        # Guardar mensaje saliente
        out_msg = Message(
            customer_id=customer.id,
            direction="outbound",
            content=ai_response,
            msg_type="text"
        )
        db.add(out_msg)
        db.commit()

        return {"status": "success"}
    except Exception as e:
        print(f"ERROR en webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
