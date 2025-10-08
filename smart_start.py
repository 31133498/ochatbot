"""
Smart OpportunityBot with AI Analysis
No API keys needed - uses free text processing!
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime
from ai_analyzer import FreeOpportunityAnalyzer

app = FastAPI(title="OpportunityBot - Smart Version with AI")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI analyzer
analyzer = FreeOpportunityAnalyzer()

# Create enhanced database
def init_db():
    conn = sqlite3.connect('smart_opportunities.db')
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
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Smart database initialized!")

@app.get("/")
async def root():
    return {"message": "OpportunityBot Smart Version is running! 🤖🚀"}

@app.get("/opportunities")
async def get_opportunities():
    conn = sqlite3.connect('smart_opportunities.db')
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
            "status": row[10],
            "created_at": row[11]
        })
    
    return opportunities

@app.post("/opportunities")
async def create_opportunity(data: dict):
    content = data.get("content", "")
    
    # 🤖 AI ANALYSIS - Extract everything automatically!
    analysis = analyzer.analyze_opportunity(content)
    
    title = analysis.get("title", "Untitled Opportunity")
    category = analysis.get("category", "general")
    deadline = analysis.get("deadline")
    requirements = '|'.join(analysis.get("requirements", []))
    contact_info = str(analysis.get("contact_info", {}))
    priority_score = analysis.get("priority_score", 5.0)
    compensation = analysis.get("compensation")
    location = analysis.get("location")
    
    conn = sqlite3.connect('smart_opportunities.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO opportunities 
        (title, content, category, deadline, requirements, contact_info, 
         priority_score, compensation, location) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, content, category, deadline, requirements, contact_info, 
          priority_score, compensation, location))
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
        "status": "new",
        "message": "🤖 Opportunity analyzed and saved with AI!",
        "ai_analysis": {
            "extracted_title": title,
            "detected_category": category,
            "found_deadline": deadline,
            "priority_score": f"{priority_score}/10",
            "requirements_found": len(analysis.get("requirements", [])),
            "contact_info_found": bool(analysis.get("contact_info"))
        }
    }

@app.put("/opportunities/{opportunity_id}/status")
async def update_status(opportunity_id: int, data: dict):
    status = data.get("status", "new")
    
    conn = sqlite3.connect('smart_opportunities.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE opportunities SET status = ? WHERE id = ?', (status, opportunity_id))
    conn.commit()
    conn.close()
    
    return {"message": f"Status updated to: {status}"}

@app.get("/stats")
async def get_stats():
    conn = sqlite3.connect('smart_opportunities.db')
    cursor = conn.cursor()
    
    # Get various statistics
    cursor.execute('SELECT COUNT(*) FROM opportunities')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE category = "job"')
    jobs = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE status = "new"')
    new_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE priority_score >= 8')
    high_priority = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE deadline IS NOT NULL')
    with_deadlines = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_opportunities": total,
        "job_opportunities": jobs,
        "new_opportunities": new_count,
        "high_priority": high_priority,
        "with_deadlines": with_deadlines
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting OpportunityBot Smart Version...")
    print("✨ Features: AI Analysis, Priority Scoring, Deadline Detection")
    print("📊 Dashboard: http://localhost:8000/docs")
    print("🔗 API: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)