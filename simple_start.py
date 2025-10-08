"""
Simple starter script to test the basic system
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime

app = FastAPI(title="OpportunityBot - Simple Version")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create simple database
def init_db():
    conn = sqlite3.connect('opportunities.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Database initialized!")

@app.get("/")
async def root():
    return {"message": "OpportunityBot is running! 🚀"}

@app.get("/opportunities")
async def get_opportunities():
    conn = sqlite3.connect('opportunities.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM opportunities ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    opportunities = []
    for row in rows:
        opportunities.append({
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "category": row[3],
            "status": row[4],
            "created_at": row[5]
        })
    
    return opportunities

@app.post("/opportunities")
async def create_opportunity(data: dict):
    title = data.get("title", "Untitled Opportunity")
    content = data.get("content", "")
    category = data.get("category", "general")
    
    conn = sqlite3.connect('opportunities.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO opportunities (title, content, category) VALUES (?, ?, ?)',
        (title, content, category)
    )
    conn.commit()
    opportunity_id = cursor.lastrowid
    conn.close()
    
    return {
        "id": opportunity_id,
        "title": title,
        "content": content,
        "category": category,
        "status": "new",
        "message": "Opportunity saved successfully!"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting OpportunityBot...")
    print("📊 Dashboard will be at: http://localhost:8000/docs")
    print("🔗 API will be at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)