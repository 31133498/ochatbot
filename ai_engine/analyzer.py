import openai
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class OpportunityAnalyzer:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    async def analyze_opportunity(self, content: str) -> Dict:
        """Analyze opportunity content and extract structured data"""
        
        prompt = f"""
        Analyze this opportunity text and extract the following information in JSON format:
        
        Text: "{content}"
        
        Extract:
        1. title: A concise title for this opportunity
        2. category: One of [job, freelance, business, grant, competition, internship, other]
        3. deadline: Extract any deadline/due date (format: YYYY-MM-DD HH:MM:SS or null)
        4. requirements: List of key requirements/qualifications
        5. contact_info: Extract email, phone, website, company name
        6. priority_score: Rate urgency/importance 1-10 (10=highest)
        7. location: Extract location if mentioned
        8. compensation: Extract salary/payment info if mentioned
        
        Return only valid JSON format.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            # Parse JSON response
            import json
            analysis = json.loads(result)
            
            # Post-process deadline
            if analysis.get("deadline"):
                analysis["deadline"] = self._parse_deadline(analysis["deadline"])
                
            return analysis
            
        except Exception as e:
            # Fallback analysis
            return self._fallback_analysis(content)
    
    def _parse_deadline(self, deadline_str: str) -> Optional[datetime]:
        """Parse deadline string to datetime object"""
        try:
            # Try different date formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(deadline_str, fmt)
                except ValueError:
                    continue
                    
        except Exception:
            pass
        return None
    
    def _fallback_analysis(self, content: str) -> Dict:
        """Fallback analysis without AI"""
        
        # Simple keyword-based analysis
        categories = {
            "job": ["job", "position", "role", "hiring", "employment"],
            "freelance": ["freelance", "contract", "gig", "project"],
            "business": ["business", "partnership", "investment", "startup"],
            "grant": ["grant", "funding", "scholarship", "award"]
        }
        
        category = "other"
        for cat, keywords in categories.items():
            if any(keyword in content.lower() for keyword in keywords):
                category = cat
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        
        # Extract phone
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, content)
        
        return {
            "title": content[:50] + "..." if len(content) > 50 else content,
            "category": category,
            "deadline": None,
            "requirements": [],
            "contact_info": {
                "emails": emails,
                "phones": phones
            },
            "priority_score": 5.0,
            "location": None,
            "compensation": None
        }