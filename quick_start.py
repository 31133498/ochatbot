"""
Quick Start - Minimal OpportunityBot with Dark Dashboard
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import json
from datetime import datetime

app = FastAPI(title="OpportunityBot")

# CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect('opportunities.db')
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
            priority_score INTEGER DEFAULT 5,
            status TEXT DEFAULT 'new',
            compensation TEXT,
            location TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add sample data if empty
    cursor.execute('SELECT COUNT(*) FROM opportunities')
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Senior Python Developer", "Remote Python developer position at TechCorp. Full-time role with competitive salary.", "tech", "2024-02-15", '["Python", "FastAPI", "PostgreSQL"]', '{"email": "hr@techcorp.com"}', 8, "new", "$80,000-$120,000", "Remote"),
            ("Freelance Web Design", "Need a modern website for small business. WordPress preferred.", "freelance", "2024-02-10", '["WordPress", "CSS", "JavaScript"]', '{"phone": "+1234567890"}', 6, "applied", "$2,000-$5,000", "Local"),
            ("Data Analyst Internship", "Summer internship program at DataCorp. Great learning opportunity.", "internship", "2024-03-01", '["Excel", "Python", "SQL"]', '{"website": "datacorp.com/careers"}', 7, "interview", "Unpaid", "New York")
        ]
        
        cursor.executemany(
            'INSERT INTO opportunities (title, content, category, deadline, requirements, contact_info, priority_score, status, compensation, location) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            sample_data
        )
    
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ OpportunityBot started!")
    print("🌐 Dashboard: http://localhost:8000")
    print("📡 API Docs: http://localhost:8000/docs")

@app.get("/")
async def dashboard():
    return FileResponse("dark_table_dashboard.html")

@app.get("/opportunities")
async def get_opportunities():
    conn = sqlite3.connect('opportunities.db')
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
            "requirements": json.loads(row[5]) if row[5] else [],
            "contact_info": row[6],
            "priority_score": row[7],
            "status": row[8],
            "compensation": row[9],
            "location": row[10],
            "created_at": row[11]
        })
    
    return opportunities

@app.post("/opportunities")
async def create_opportunity(data: dict):
    content = data.get("content", "")
    
    # Simple AI analysis (you can enhance this later)
    title = content.split('\n')[0][:100] if content else "New Opportunity"
    category = "general"
    priority_score = 5
    
    # Extract basic info
    if any(word in content.lower() for word in ["urgent", "asap", "immediate"]):
        priority_score = 9
    elif any(word in content.lower() for word in ["senior", "lead", "manager"]):
        priority_score = 7
    
    if any(word in content.lower() for word in ["python", "developer", "engineer"]):
        category = "tech"
    elif any(word in content.lower() for word in ["freelance", "contract"]):
        category = "freelance"
    
    conn = sqlite3.connect('opportunities.db')
    cursor = conn.cursor()
    cursor.execute(
        '''INSERT INTO opportunities 
           (title, content, category, priority_score) 
           VALUES (?, ?, ?, ?)''',
        (title, content, category, priority_score)
    )
    conn.commit()
    opportunity_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": opportunity_id,
        "title": title,
        "content": content,
        "category": category,
        "priority_score": priority_score,
        "status": "new",
        "message": "Opportunity analyzed and saved!"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)