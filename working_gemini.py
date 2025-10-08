"""
Working Gemini AI OpportunityBot - Simplified and Robust
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime
import os
from dotenv import load_dotenv

# Try to import Gemini, fallback if not available
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()

app = FastAPI(title="OpportunityBot - Working Gemini Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini if available
gemini_model = None
if GEMINI_AVAILABLE:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your-gemini-key-here":
        try:
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI initialized successfully!")
        except Exception as e:
            print(f"⚠️ Gemini initialization failed: {e}")
            gemini_model = None
    else:
        print("⚠️ No valid Gemini API key found")
else:
    print("⚠️ Gemini library not installed")

def init_db():
    conn = sqlite3.connect('working_opportunities.db')
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

def analyze_with_gemini(content: str) -> dict:
    """Analyze with Gemini AI"""
    if not gemini_model:
        return analyze_basic(content)
    
    try:
        prompt = f"""
Extract information from this opportunity text and return ONLY valid JSON:

"{content}"

{{
  "title": "Senior Full-Stack Developer at TechCorp",
  "category": "job",
  "deadline": "2025-01-25",
  "requirements": ["5+ years React", "Node.js", "PostgreSQL", "AWS"],
  "contact_info": {{"emails": ["sarah@techcorp.com"], "phones": ["415-555-0123"]}},
  "priority_score": 9.0,
  "compensation": "$140k-200k + equity",
  "location": "San Francisco (Remote OK)",
  "summary": "Urgent senior developer role with CTO potential"
}}

Rules:
- Extract exact deadline dates (January 25, 2025 = "2025-01-25")
- Find all requirements after "Requirements:" or "Must have:"
- Priority 8-10 for urgent/senior roles, 6-7 for good roles, 1-5 for basic
- Include salary ranges and equity if mentioned
- Return ONLY the JSON, no other text
"""
        
        response = gemini_model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean JSON response
        if result_text.startswith('```json'):
            result_text = result_text[7:-3]
        elif result_text.startswith('```'):
            result_text = result_text[3:-3]
        
        import json
        result = json.loads(result_text)
        
        # Validate result
        return {
            "title": result.get("title", "Untitled Opportunity")[:100],
            "category": result.get("category", "other"),
            "deadline": result.get("deadline"),
            "requirements": result.get("requirements", [])[:5],
            "contact_info": result.get("contact_info", {}),
            "priority_score": max(1.0, min(10.0, float(result.get("priority_score", 5.0)))),
            "compensation": result.get("compensation"),
            "location": result.get("location"),
            "summary": result.get("summary", "")[:200]
        }
        
    except Exception as e:
        print(f"Gemini error: {e}")
        return analyze_basic(content)

def analyze_basic(content: str) -> dict:
    """Basic fallback analysis"""
    import re
    
    # Simple title extraction
    title = content.split('\n')[0][:100] if content else "Untitled Opportunity"
    
    # Simple category detection
    content_lower = content.lower()
    if any(word in content_lower for word in ['job', 'position', 'role', 'hiring']):
        category = 'job'
    elif any(word in content_lower for word in ['freelance', 'contract', 'gig']):
        category = 'freelance'
    else:
        category = 'other'
    
    # Extract email
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    
    # Extract phone
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
    
    # Simple priority scoring
    priority = 5.0
    if any(word in content_lower for word in ['urgent', 'asap', 'immediate']):
        priority += 2.0
    if any(word in content_lower for word in ['senior', 'lead', 'manager']):
        priority += 1.0
    
    return {
        "title": title,
        "category": category,
        "deadline": None,
        "requirements": [],
        "contact_info": {"emails": emails, "phones": phones},
        "priority_score": min(10.0, priority),
        "compensation": None,
        "location": None,
        "summary": f"Basic analysis of {category} opportunity"
    }

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ Database initialized!")

@app.get("/")
async def root():
    status = "with Gemini AI" if gemini_model else "with Basic Analysis"
    return {"message": f"OpportunityBot {status} is running! 🤖"}

@app.get("/opportunities")
async def get_opportunities():
    conn = sqlite3.connect('working_opportunities.db')
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
    try:
        content = data.get("content", "")
        
        # Analyze with Gemini or fallback
        if gemini_model:
            analysis = analyze_with_gemini(content)
            ai_type = "Gemini AI"
        else:
            analysis = analyze_basic(content)
            ai_type = "Basic Analysis"
        
        # Save to database
        conn = sqlite3.connect('working_opportunities.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO opportunities 
            (title, content, category, deadline, requirements, contact_info, 
             priority_score, compensation, location, summary) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis["title"],
            content,
            analysis["category"],
            analysis["deadline"],
            '|'.join(analysis["requirements"]) if analysis["requirements"] else "",
            str(analysis["contact_info"]),
            analysis["priority_score"],
            analysis["compensation"],
            analysis["location"],
            analysis["summary"]
        ))
        
        conn.commit()
        opportunity_id = cursor.lastrowid
        conn.close()
        
        return {
            "id": opportunity_id,
            "message": f"✅ Opportunity analyzed with {ai_type}!",
            "analysis": analysis,
            "ai_used": ai_type
        }
        
    except Exception as e:
        return {
            "error": f"Analysis failed: {str(e)}",
            "message": "Please try again with simpler content"
        }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting Working OpportunityBot...")
    print("📊 Dashboard: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)