"""
Free AI Analyzer using simple text processing
No API keys needed!
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class FreeOpportunityAnalyzer:
    def __init__(self):
        self.categories = {
            "job": ["job", "position", "role", "hiring", "employment", "career", "work", "developer", "engineer", "manager"],
            "freelance": ["freelance", "contract", "gig", "project", "consultant", "independent"],
            "business": ["business", "partnership", "investment", "startup", "entrepreneur", "venture"],
            "grant": ["grant", "funding", "scholarship", "award", "fellowship", "sponsorship"],
            "competition": ["competition", "contest", "hackathon", "challenge", "tournament"]
        }
        
        self.deadline_patterns = [
            r'deadline[:\s]*([^.\n]+)',
            r'due[:\s]*([^.\n]+)',
            r'apply by[:\s]*([^.\n]+)',
            r'closes[:\s]*([^.\n]+)',
            r'expires[:\s]*([^.\n]+)'
        ]
        
        self.salary_patterns = [
            r'\$[\d,]+(?:k|,000)?(?:\s*-\s*\$[\d,]+(?:k|,000)?)?',
            r'salary[:\s]*\$?[\d,]+(?:k|,000)?',
            r'budget[:\s]*\$?[\d,]+(?:k|,000)?',
            r'pay[:\s]*\$?[\d,]+(?:k|,000)?'
        ]

    def analyze_opportunity(self, content: str) -> Dict:
        """Analyze opportunity content and extract structured data"""
        
        content_lower = content.lower()
        
        # Extract title (first sentence or first 50 chars)
        title = self._extract_title(content)
        
        # Detect category
        category = self._detect_category(content_lower)
        
        # Extract deadline
        deadline = self._extract_deadline(content)
        
        # Extract requirements
        requirements = self._extract_requirements(content)
        
        # Extract contact info
        contact_info = self._extract_contact_info(content)
        
        # Calculate priority score
        priority_score = self._calculate_priority(content_lower, deadline)
        
        # Extract salary/compensation
        compensation = self._extract_compensation(content)
        
        return {
            "title": title,
            "category": category,
            "deadline": deadline,
            "requirements": requirements,
            "contact_info": contact_info,
            "priority_score": priority_score,
            "compensation": compensation,
            "location": self._extract_location(content)
        }

    def _extract_title(self, content: str) -> str:
        """Extract a meaningful title from content"""
        lines = content.strip().split('\n')
        first_line = lines[0].strip()
        
        # If first line is short and looks like a title
        if len(first_line) < 100 and first_line:
            return first_line
        
        # Otherwise, take first 50 characters
        return content[:50].strip() + "..." if len(content) > 50 else content.strip()

    def _detect_category(self, content_lower: str) -> str:
        """Detect opportunity category based on keywords"""
        category_scores = {}
        
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "other"

    def _extract_deadline(self, content: str) -> Optional[str]:
        """Extract deadline from content"""
        for pattern in self.deadline_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                deadline_text = match.group(1).strip()
                # Try to parse common date formats
                parsed_date = self._parse_date(deadline_text)
                if parsed_date:
                    return parsed_date.strftime("%Y-%m-%d")
        
        return None

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse various date formats"""
        date_text = date_text.lower().strip()
        
        # Common date patterns
        patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{1,2})-(\d{1,2})-(\d{4})',  # MM-DD-YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
        ]
        
        for pattern in patterns:
            match = re.search(pattern, date_text)
            if match:
                try:
                    if len(match.group(1)) == 4:  # YYYY-MM-DD
                        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    else:  # MM/DD/YYYY or MM-DD-YYYY
                        return datetime(int(match.group(3)), int(match.group(1)), int(match.group(2)))
                except ValueError:
                    continue
        
        # Handle relative dates
        if 'tomorrow' in date_text:
            return datetime.now() + timedelta(days=1)
        elif 'next week' in date_text:
            return datetime.now() + timedelta(weeks=1)
        elif 'next month' in date_text:
            return datetime.now() + timedelta(days=30)
        
        return None

    def _extract_requirements(self, content: str) -> List[str]:
        """Extract requirements from content"""
        requirements = []
        
        # Look for requirement keywords
        req_patterns = [
            r'requirements?[:\s]*([^.\n]+)',
            r'qualifications?[:\s]*([^.\n]+)',
            r'skills?[:\s]*([^.\n]+)',
            r'experience[:\s]*([^.\n]+)',
            r'must have[:\s]*([^.\n]+)'
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                # Split by common separators
                items = re.split(r'[,;•\n]', match)
                for item in items:
                    item = item.strip()
                    if item and len(item) > 3:
                        requirements.append(item)
        
        return requirements[:5]  # Limit to 5 requirements

    def _extract_contact_info(self, content: str) -> Dict:
        """Extract contact information"""
        contact_info = {}
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        if emails:
            contact_info['emails'] = emails
        
        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, content)
        if phones:
            contact_info['phones'] = phones
        
        # Extract websites
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, content)
        if urls:
            contact_info['websites'] = urls
        
        return contact_info

    def _extract_compensation(self, content: str) -> Optional[str]:
        """Extract salary/compensation information"""
        for pattern in self.salary_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _extract_location(self, content: str) -> Optional[str]:
        """Extract location information"""
        location_patterns = [
            r'location[:\s]*([^.\n]+)',
            r'based in[:\s]*([^.\n]+)',
            r'remote',
            r'work from home',
            r'onsite'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if pattern in ['remote', 'work from home']:
                    return 'Remote'
                elif pattern == 'onsite':
                    return 'On-site'
                else:
                    return match.group(1).strip()
        
        return None

    def _calculate_priority(self, content_lower: str, deadline: Optional[str]) -> float:
        """Calculate priority score based on content and deadline"""
        score = 5.0  # Base score
        
        # Increase score for urgent keywords
        urgent_keywords = ['urgent', 'asap', 'immediate', 'rush', 'priority']
        for keyword in urgent_keywords:
            if keyword in content_lower:
                score += 1.0
        
        # Increase score for high-value keywords
        value_keywords = ['senior', 'lead', 'manager', 'director', 'high salary', 'competitive']
        for keyword in value_keywords:
            if keyword in content_lower:
                score += 0.5
        
        # Adjust based on deadline
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                days_until = (deadline_date - datetime.now()).days
                if days_until <= 3:
                    score += 2.0
                elif days_until <= 7:
                    score += 1.0
                elif days_until <= 14:
                    score += 0.5
            except ValueError:
                pass
        
        return min(10.0, max(1.0, score))  # Keep between 1-10