from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class OpportunityBase(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"
    deadline: Optional[datetime] = None
    requirements: Optional[List[str]] = []
    contact_info: Optional[Dict[str, Any]] = None
    priority_score: Optional[float] = 5.0
    status: Optional[str] = "new"
    source: Optional[str] = "whatsapp"

class OpportunityCreate(BaseModel):
    content: str
    source: Optional[str] = "whatsapp"

class OpportunityResponse(OpportunityBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True