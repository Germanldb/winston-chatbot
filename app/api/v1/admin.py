from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...database import get_db
from ...models.models import Customer, Message, BotStats
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    total_messages = db.query(Message).count()
    total_customers = db.query(Customer).count()
    
    # Messages in last 24h
    last_24h = datetime.utcnow() - timedelta(hours=24)
    messages_24h = db.query(Message).filter(Message.timestamp >= last_24h).count()
    
    # Group by type
    msg_types = db.query(Message.msg_type, func.count(Message.id)).group_by(Message.msg_type).all()
    
    return {
        "total_messages": total_messages,
        "total_customers": total_customers,
        "messages_24h": messages_24h,
        "types": dict(msg_types)
    }

@router.get("/messages")
async def get_recent_messages(limit: int = 50, db: Session = Depends(get_db)):
    messages = db.query(Message).order_by(Message.timestamp.desc()).limit(limit).all()
    return [{
        "id": m.id,
        "customer": m.customer.name or m.customer.whatsapp_id,
        "content": m.content,
        "direction": m.direction,
        "timestamp": m.timestamp,
        "type": m.msg_type
    } for m in messages]
