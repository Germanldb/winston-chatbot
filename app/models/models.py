from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("Message", back_populates="customer")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    direction = Column(String)  # 'inbound' or 'outbound'
    content = Column(Text)
    msg_type = Column(String)  # 'text', 'image', etc.
    media_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="messages")

class BotStats(Base):
    __tablename__ = "bot_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String) # 'message_received', 'message_sent', 'image_processed'
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
