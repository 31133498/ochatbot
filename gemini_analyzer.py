"""
Gemini AI Analyzer - FREE and POWERFUL!
"""
import google.generativeai as genai
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GeminiOpportunityAnalyzer:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your-gemini-key-here":
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.use_ai = True
            print("✅ Gemini AI initialized!")
        else:
            self.use_ai = False
            print("⚠️ No Gemini key found, using basic analysis")
            # Fallback to basic analyzer
            from ai_analyzer import FreeOpportunityAnalyzer
            self.fallback = FreeOpportunityAnalyzer()

    def analyze_opportunity(self, content: str) -> dict:
        """Analyze opportunity using Gemini AI or fallback"""
        
        if not self.use_ai:
            return self.fallback.analyze_opportunity(content)
        
        try:
            return self._analyze_with_gemini(content)
        except Exception as e:
            print(f"Gemini error: {e}, using fallback")
            return self.fallback.analyze_opportunity(content)

    def _analyze_with_gemini(self, content: str) -> dict:
        """Use Gemini AI for advanced analysis"""
        
        prompt = f"""
Analyze this opportunity text and extract information in JSON format:

TEXT: "{content}"

Extract and return ONLY valid JSON with these fields:
{{
  "title": "A clear, concise title for this opportunity",
  "category": "One of: job, freelance, business, grant, competition, internship, other",
  "deadline": "Date in YYYY-MM-DD format or null if not found",
  "requirements": ["List of key requirements/skills needed"],
  "contact_info": {{
    "emails": ["email addresses found"],
    "phones": ["phone numbers found"],
    "websites": ["websites found"],
    "company": "company name if mentioned"
  }},
  "priority_score": 7.5,
  "compensation": "salary/payment info if mentioned or null",
  "location": "location/remote info or null",
  "summary": "Brief 1-sentence summary"
}}

Priority score rules:
- 1-3: Low priority/interest
- 4-6: Medium priority
- 7-8: High priority (good match, urgent, or high value)
- 9-10: Extremely high priority (perfect match, urgent deadline, exceptional opportunity)

Consider: urgency keywords, salary level, seniority, deadline proximity, requirements match.

Return ONLY the JSON, no other text.
"""

        response = self.model.generate_content(prompt)
        
        try:
            # Clean the response and parse JSON
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            
            # Validate and clean the result
            return self._validate_result(result)
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response.text}")
            # Fallback to basic analysis
            return self.fallback.analyze_opportunity(content)

    def _validate_result(self, result: dict) -> dict:
        """Validate and clean the AI result"""
        
        # Ensure required fields exist
        validated = {
            "title": result.get("title", "Untitled Opportunity"),
            "category": result.get("category", "other"),
            "deadline": result.get("deadline"),
            "requirements": result.get("requirements", []),
            "contact_info": result.get("contact_info", {}),
            "priority_score": float(result.get("priority_score", 5.0)),
            "compensation": result.get("compensation"),
            "location": result.get("location"),
            "summary": result.get("summary", "")
        }
        
        # Validate category
        valid_categories = ["job", "freelance", "business", "grant", "competition", "internship", "other"]
        if validated["category"] not in valid_categories:
            validated["category"] = "other"
        
        # Validate priority score
        validated["priority_score"] = max(1.0, min(10.0, validated["priority_score"]))
        
        # Validate deadline format
        if validated["deadline"]:
            try:
                datetime.strptime(validated["deadline"], "%Y-%m-%d")
            except ValueError:
                validated["deadline"] = None
        
        return validated