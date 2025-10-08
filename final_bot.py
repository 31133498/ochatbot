"""
Final OpportunityBot - Bulletproof with Smart Analysis
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import sqlite3
from datetime import datetime
import os
import re
from dotenv import load_dotenv

# Try Gemini import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

load_dotenv()

app = FastAPI(title="OpportunityBot - Final Version")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
gemini_model = None
if GEMINI_AVAILABLE:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your-gemini-key-here":
        try:
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("[OK] Gemini AI ready!")
        except:
            print("[WARNING] Gemini setup failed")

def init_db():
    conn = sqlite3.connect('final_opportunities.db')
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

def smart_analyze(content: str) -> dict:
    """Smart analysis combining Gemini + Enhanced Basic"""
    
    # Enhanced basic analysis first
    basic = enhanced_basic_analysis(content)
    
    # Try Gemini enhancement
    if gemini_model:
        try:
            gemini_result = gemini_enhance(content, basic)
            if gemini_result:
                return gemini_result
        except Exception as e:
            print(f"Gemini failed: {e}")
    
    return basic

def enhanced_basic_analysis(content: str) -> dict:
    """Enhanced basic analysis with better extraction"""
    
    # Smart title extraction
    lines = content.strip().split('.')
    title = lines[0].strip()
    if len(title) > 80:
        title = title[:80] + "..."
    
    # Category detection
    content_lower = content.lower()
    if any(word in content_lower for word in ['job', 'position', 'role', 'hiring', 'developer', 'engineer', 'manager']):
        category = 'job'
    elif any(word in content_lower for word in ['freelance', 'contract', 'gig', 'project']):
        category = 'freelance'
    elif any(word in content_lower for word in ['business', 'startup', 'investment']):
        category = 'business'
    else:
        category = 'other'
    
    # Enhanced deadline extraction
    deadline = extract_deadline(content)
    
    # Enhanced requirements extraction
    requirements = extract_requirements(content)
    
    # Contact info extraction
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', content)
    websites = re.findall(r'https?://[^\s]+', content)
    
    # Enhanced compensation extraction
    compensation = extract_compensation(content)
    
    # Location extraction
    location = extract_location(content)
    
    # Smart priority scoring
    priority = calculate_smart_priority(content_lower, deadline, compensation)
    
    return {
        "title": title,
        "category": category,
        "deadline": deadline,
        "requirements": requirements,
        "contact_info": {"emails": emails, "phones": phones, "websites": websites},
        "priority_score": priority,
        "compensation": compensation,
        "location": location,
        "summary": f"Smart analysis: {category} opportunity with {len(requirements)} requirements"
    }

def extract_deadline(content: str) -> str:
    """Enhanced deadline extraction"""
    patterns = [
        r'deadline[:\s]*([^.\n!]+)',
        r'due[:\s]*([^.\n!]+)',
        r'apply by[:\s]*([^.\n!]+)',
        r'closes[:\s]*([^.\n!]+)',
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}',
        r'\d{1,2}/\d{1,2}/\d{4}',
        r'\d{4}-\d{1,2}-\d{1,2}'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            date_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
            parsed = parse_date_smart(date_text)
            if parsed:
                return parsed
    return None

def parse_date_smart(date_text: str) -> str:
    """Smart date parsing"""
    date_text = date_text.strip().lower()
    
    # Handle "February 10, 2025" format
    month_map = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }
    
    for month_name, month_num in month_map.items():
        if month_name in date_text:
            # Extract day and year
            day_match = re.search(r'\b(\d{1,2})\b', date_text)
            year_match = re.search(r'\b(20\d{2})\b', date_text)
            if day_match and year_match:
                return f"{year_match.group(1)}-{month_num:02d}-{int(day_match.group(1)):02d}"
    
    # Handle MM/DD/YYYY
    date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_text)
    if date_match:
        month, day, year = date_match.groups()
        return f"{year}-{int(month):02d}-{int(day):02d}"
    
    return None

def extract_requirements(content: str) -> list:
    """Enhanced requirements extraction"""
    requirements = []
    
    # Look for requirements sections
    req_patterns = [
        r'requirements?[:\s]*([^.!]+)',
        r'qualifications?[:\s]*([^.!]+)',
        r'skills?[:\s]*([^.!]+)',
        r'experience[:\s]*([^.!]+)',
        r'must have[:\s]*([^.!]+)',
        r'need someone with[:\s]*([^.!]+)'
    ]
    
    for pattern in req_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            # Split by common separators
            items = re.split(r'[,;•\n]|and\s+', match)
            for item in items:
                item = item.strip()
                if len(item) > 3 and len(item) < 50:
                    requirements.append(item)
    
    return requirements[:5]

def extract_compensation(content: str) -> str:
    """Enhanced compensation extraction"""
    patterns = [
        r'salary[:\s]*\$?[\d,]+k?(?:\s*-\s*\$?[\d,]+k?)?(?:\s*\+\s*\w+)?',
        r'\$[\d,]+k?(?:\s*-\s*\$[\d,]+k?)?(?:\s*\+\s*\w+)?',
        r'budget[:\s]*\$?[\d,]+k?',
        r'pay[:\s]*\$?[\d,]+k?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def extract_location(content: str) -> str:
    """Enhanced location extraction"""
    if re.search(r'\bremote\b', content, re.IGNORECASE):
        return "Remote"
    
    # Look for city names
    location_match = re.search(r'\bin\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', content)
    if location_match:
        return location_match.group(1)
    
    return None

def calculate_smart_priority(content_lower: str, deadline: str, compensation: str) -> float:
    """Smart priority calculation"""
    score = 5.0
    
    # Urgency boost
    if any(word in content_lower for word in ['urgent', 'asap', 'immediate', 'rush']):
        score += 2.0
    
    # Seniority boost
    if any(word in content_lower for word in ['senior', 'lead', 'manager', 'director', 'cto']):
        score += 1.5
    
    # Compensation boost
    if compensation:
        if any(num in compensation for num in ['100k', '120k', '140k', '150k', '200k']):
            score += 1.0
        if 'equity' in compensation.lower():
            score += 0.5
    
    # Deadline proximity boost
    if deadline:
        try:
            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
            days_until = (deadline_date - datetime.now()).days
            if days_until <= 7:
                score += 1.0
            elif days_until <= 30:
                score += 0.5
        except:
            pass
    
    return min(10.0, score)

def gemini_enhance(content: str, basic: dict) -> dict:
    """Use Gemini to enhance basic analysis"""
    try:
        prompt = f"""Improve this analysis of an opportunity. Return ONLY JSON:

Original text: "{content}"

Current analysis: {basic}

Improve the title, extract better requirements, find exact deadline, improve summary.
Return JSON with same structure but better data.
"""
        
        response = gemini_model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Clean response
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0]
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0]
        
        import json
        enhanced = json.loads(result_text)
        
        # Merge with basic analysis
        return {**basic, **enhanced}
        
    except Exception as e:
        print(f"Gemini enhance failed: {e}")
        return basic

@app.on_event("startup")
async def startup():
    init_db()
    print("[OK] Final OpportunityBot ready!")

@app.get("/")
async def dashboard():
    return FileResponse("dark_table_dashboard.html")

@app.get("/api")
async def root():
    ai_status = "with Gemini AI" if gemini_model else "with Enhanced Analysis"
    return {"message": f"Final OpportunityBot {ai_status} is running! 🚀"}

@app.get("/opportunities")
async def get_opportunities():
    conn = sqlite3.connect('final_opportunities.db')
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
        
        # Smart analysis
        analysis = smart_analyze(content)
        
        # Save to database
        conn = sqlite3.connect('final_opportunities.db')
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
        
        ai_type = "Gemini Enhanced" if gemini_model else "Smart Analysis"
        
        return {
            "id": opportunity_id,
            "message": f"✅ Opportunity analyzed with {ai_type}!",
            "analysis": analysis,
            "ai_used": ai_type
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    print("[STARTING] Final OpportunityBot...")
    uvicorn.run(app, host="0.0.0.0", port=8000)