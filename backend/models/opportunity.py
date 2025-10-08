from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Opportunity(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), default="general")
    deadline = Column(DateTime, nullable=True)
    requirements = Column(JSON, default=list)
    contact_info = Column(JSON, nullable=True)
    priority_score = Column(Float, default=5.0)
    status = Column(String(50), default="new")  # new, applied, in_progress, completed, rejected
    source = Column(String(50), default="whatsapp")  # whatsapp, manual, email
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, title='{self.title}', category='{self.category}')>"