"""
WhatsApp OpportunityBot - Complete Integration
"""
from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
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

app = FastAPI(title="OpportunityBot WhatsApp Integration")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Twilio
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Initialize Gemini
gemini_model = None
if GEMINI_AVAILABLE:
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your-gemini-key-here":
        try:
            genai.configure(api_key=api_key)
            gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI ready for WhatsApp!")
        except:
            print("⚠️ Gemini setup failed")

def init_db():
    conn = sqlite3.connect('whatsapp_opportunities.db')
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
            source TEXT DEFAULT 'whatsapp',
            phone_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def analyze_opportunity(content: str) -> dict:
    """Analyze opportunity with Gemini or fallback"""
    
    if gemini_model:
        try:
            prompt = f"""
Analyze this opportunity and return JSON:

"{content}"

{{
  "title": "Clear title",
  "category": "job/freelance/business/grant/other",
  "deadline": "2025-01-25 or null",
  "requirements": ["skill1", "skill2"],
  "contact_info": {{"emails": ["email"], "phones": ["phone"]}},
  "priority_score": 8.5,
  "compensation": "$salary or null",
  "location": "location or null",
  "summary": "Brief summary"
}}

Return only JSON.
"""
            
            response = gemini_model.generate_content(prompt)
            result_text = response.text.strip()
            
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            import json
            return json.loads(result_text)
            
        except Exception as e:
            print(f"Gemini error: {e}")
    
    # Fallback analysis
    return {
        "title": content[:50] + "..." if len(content) > 50 else content,
        "category": "job" if any(word in content.lower() for word in ['job', 'position', 'role']) else "other",
        "deadline": None,
        "requirements": [],
        "contact_info": {"emails": [], "phones": []},
        "priority_score": 6.0 if 'urgent' in content.lower() else 5.0,
        "compensation": None,
        "location": None,
        "summary": "Opportunity received via WhatsApp"
    }

@app.on_event("startup")
async def startup():
    init_db()
    print("✅ WhatsApp OpportunityBot ready!")
    print(f"📱 Twilio Account: {os.getenv('TWILIO_ACCOUNT_SID', 'Not configured')}")

@app.get("/")
async def root():
    return {
        "message": "📱 WhatsApp OpportunityBot is running!",
        "status": "Ready to receive opportunities via WhatsApp",
        "gemini_ai": "Enabled" if gemini_model else "Disabled"
    }

@app.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    
    form_data = await request.form()
    
    from_number = form_data.get("From", "")
    message_body = form_data.get("Body", "")
    media_url = form_data.get("MediaUrl0", "")
    
    print(f"📱 WhatsApp message from {from_number}: {message_body[:50]}...")
    
    response = MessagingResponse()
    
    try:
        if message_body or media_url:
            # Process media if present
            if media_url:
                content = f"Media received: {media_url}\n{message_body}"
            else:
                content = message_body
            
            # Analyze with AI
            analysis = analyze_opportunity(content)
            
            # Save to database
            conn = sqlite3.connect('whatsapp_opportunities.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO opportunities 
                (title, content, category, deadline, requirements, contact_info, 
                 priority_score, compensation, location, summary, phone_number) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                analysis["summary"],
                from_number
            ))
            
            conn.commit()
            opportunity_id = cursor.lastrowid
            conn.close()
            
            # Send confirmation
            ai_type = "🤖 Gemini AI" if gemini_model else "🔍 Smart Analysis"
            
            confirmation = f"""✅ *Opportunity Saved!*

📋 *Title:* {analysis['title'][:60]}{'...' if len(analysis['title']) > 60 else ''}

🏷️ *Category:* {analysis['category'].title()}

⭐ *Priority:* {analysis['priority_score']}/10

{f"💰 *Salary:* {analysis['compensation']}" if analysis['compensation'] else ""}

{f"📍 *Location:* {analysis['location']}" if analysis['location'] else ""}

{f"⏰ *Deadline:* {analysis['deadline']}" if analysis['deadline'] else ""}

🔢 *ID:* #{opportunity_id}

Analyzed by {ai_type}

View all opportunities in your dashboard! 📊"""
            
            response.message(confirmation)
            
        else:
            # Welcome message
            welcome = """🤖 *Welcome to OpportunityBot!*

Send me any opportunity details and I'll:
✅ Extract key information
✅ Set priority scores  
✅ Track deadlines
✅ Save to your dashboard

*Try sending:*
• Job postings
• Freelance projects  
• Business opportunities
• Grant applications

Just paste the text or send screenshots! 📸"""
            
            response.message(welcome)
            
    except Exception as e:
        print(f"Error processing WhatsApp message: {e}")
        response.message("❌ Sorry, there was an error processing your message. Please try again or contact support.")
    
    return str(response)

@app.get("/opportunities")
async def get_opportunities():
    """Get all opportunities for dashboard"""
    conn = sqlite3.connect('whatsapp_opportunities.db')
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
            "source": row[12],
            "phone_number": row[13],
            "created_at": row[14]
        })
    
    return opportunities

@app.post("/opportunities")
async def create_opportunity_manual(data: dict):
    """Manual opportunity creation (for dashboard)"""
    try:
        content = data.get("content", "")
        analysis = analyze_opportunity(content)
        
        conn = sqlite3.connect('whatsapp_opportunities.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO opportunities 
            (title, content, category, deadline, requirements, contact_info, 
             priority_score, compensation, location, summary, source) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            analysis["summary"],
            "manual"
        ))
        
        conn.commit()
        opportunity_id = cursor.lastrowid
        conn.close()
        
        return {
            "id": opportunity_id,
            "message": "✅ Opportunity analyzed and saved!",
            "analysis": analysis
        }
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

@app.get("/stats")
async def get_stats():
    """Get statistics for dashboard"""
    conn = sqlite3.connect('whatsapp_opportunities.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM opportunities')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE source = "whatsapp"')
    whatsapp_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE priority_score >= 8')
    high_priority = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM opportunities WHERE status = "applied"')
    applied = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_opportunities": total,
        "whatsapp_opportunities": whatsapp_count,
        "high_priority": high_priority,
        "applied_count": applied
    }

if __name__ == "__main__":
    import uvicorn
    print("📱 Starting WhatsApp OpportunityBot...")
    print("🔗 Webhook URL: http://localhost:8000/whatsapp")
    uvicorn.run(app, host="0.0.0.0", port=8000)