from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from backend.database.connection import get_db
from backend.models.opportunity import Opportunity
from backend.schemas.opportunity import OpportunityCreate, OpportunityResponse
from ai_engine.analyzer import OpportunityAnalyzer
from whatsapp_bot.webhook import whatsapp_router

load_dotenv()

app = FastAPI(title="OpportunityBot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(whatsapp_router, prefix="/whatsapp", tags=["WhatsApp"])

analyzer = OpportunityAnalyzer()

@app.get("/")
async def root():
    return {"message": "OpportunityBot API is running"}

@app.get("/opportunities", response_model=list[OpportunityResponse])
async def get_opportunities(db: Session = Depends(get_db)):
    opportunities = db.query(Opportunity).all()
    return opportunities

@app.post("/opportunities", response_model=OpportunityResponse)
async def create_opportunity(opportunity: OpportunityCreate, db: Session = Depends(get_db)):
    # Analyze the opportunity using AI
    analysis = await analyzer.analyze_opportunity(opportunity.content)
    
    db_opportunity = Opportunity(
        title=analysis.get("title", "Untitled Opportunity"),
        content=opportunity.content,
        category=analysis.get("category", "general"),
        deadline=analysis.get("deadline"),
        requirements=analysis.get("requirements", []),
        contact_info=analysis.get("contact_info"),
        priority_score=analysis.get("priority_score", 5),
        status="new"
    )
    
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    
    return db_opportunity

@app.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@app.put("/opportunities/{opportunity_id}/status")
async def update_opportunity_status(opportunity_id: int, status: str, db: Session = Depends(get_db)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opportunity.status = status
    db.commit()
    
    return {"message": "Status updated successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)