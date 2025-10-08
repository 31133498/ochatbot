"""
OpportunityBot with Google Gemini AI - FREE and POWERFUL!
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime
from gemini_analyzer import GeminiOpportunityAnalyzer

app = FastAPI(title="OpportunityBot - Gemini AI Powered")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini AI analyzer
analyzer = GeminiOpportunityAnalyzer()

# Create enhanced database
def init_db():
    conn = sqlite3.connect('gemini_opportunities.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            deadline TEXT,
            requirements TEXT,
            contact_info TEXT,
            priority_score REAL DEFAULT 5.0,
            compensation TEXT,
            location TEXT,
            summary TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Gemini-powered database initialized!")

@app.get("/")
async def root():
    return {"message": "OpportunityBot with Gemini AI is running! 🤖✨"}

@app.get("/opportunities")
async def get_opportunities():
    conn = sqlite3.connect('gemini_opportunities.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM opportunities ORDER BY priority_score DESC, created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    opportunities = []
    for row in rows:
        opportunities.append({
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "category": row[3],
            "deadline": row[4],
            "requirements": row[5].split('|') if row[5] else [],
            "contact_info": row[6],
            "priority_score": row[7],
            "compensation": row[8],
            "location": row[9],
            "summary": row[10],
            "status": row[11],
            "created_at": row[12]
        })
    
    return opportunities

@app.post("/opportunities")
async def create_opportunity(data: dict):
    content = data.get("content", "")
    
    # 🤖 GEMINI AI ANALYSIS - Super intelligent extraction!
    analysis = analyzer.analyze_opportunity(content)
    
    title = analysis.get("title", "Untitled Opportunity")
    category = analysis.get("category", "general")
    deadline = analysis.get("deadline")
    requirements = '|'.join(analysis.get("requirements", []))
    contact_info = str(analysis.get("contact_info", {}))
    priority_score = analysis.get("priority_score", 5.0)
    compensation = analysis.get("compensation")
    location = analysis.get("location")
    summary = analysis.get("summary", "")
    
    conn = sqlite3.connect('gemini_opportunities.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO opportunities 
        (title, content, category, deadline, requirements, contact_info, 
         priority_score, compensation, location, summary) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, content, category, deadline, requirements, contact_info, 
          priority_score, compensation, location, summary))
    conn.commit()
    opportunity_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": opportunity_id,
        "title": title,
        "content": content,
        "category": category,
        "deadline": deadline,
        "requirements": analysis.get("requirements", []),
        "contact_info": analysis.get("contact_info", {}),
        "priority_score": priority_score,
        "compensation": compensation,
        "location": location,
        "summary": summary,
        "status": "new",
        "message": "🤖 Opportunity analyzed with Gemini AI!",
        "gemini_analysis": {
            "ai_extracted_title": title,
            "ai_detected_category": category,
            "ai_found_deadline": deadline,
            "ai_priority_score": f"{priority_score}/10",
            "ai_requirements_count": len(analysis.get("requirements", [])),
            "ai_summary": summary,
            "contact_info_extracted": bool(analysis.get("contact_info"))
        }
    }

@app.get("/stats")
async def get_stats():
    conn = sqlite3.connect('gemini_opportunities.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM opportunities')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE category = "job"')
    jobs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE priority_score >= 8')
    high_priority = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(priority_score) FROM opportunities')
    avg_priority = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_opportunities": total,
        "job_opportunities": jobs,
        "high_priority_count": high_priority,
        "average_priority": round(avg_priority, 1)
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting OpportunityBot with Gemini AI...")
    print("✨ Features: Advanced AI Analysis, Smart Categorization, Priority Intelligence")
    print("📊 Dashboard: http://localhost:8000/docs")
    print("🔗 API: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)