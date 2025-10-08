from fastapi import APIRouter, Request, HTTPException
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import os
from dotenv import load_dotenv
from ai_engine.analyzer import OpportunityAnalyzer
from backend.database.connection import get_db
from backend.models.opportunity import Opportunity

load_dotenv()

whatsapp_router = APIRouter()

# Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

analyzer = OpportunityAnalyzer()

@whatsapp_router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages"""
    
    form_data = await request.form()
    
    # Extract message data
    from_number = form_data.get("From", "")
    message_body = form_data.get("Body", "")
    media_url = form_data.get("MediaUrl0", "")
    
    response = MessagingResponse()
    
    try:
        # Process the message
        if message_body or media_url:
            # If there's media, download and process it
            if media_url:
                content = await process_media(media_url)
            else:
                content = message_body
            
            # Analyze the opportunity
            analysis = await analyzer.analyze_opportunity(content)
            
            # Save to database
            db = next(get_db())
            opportunity = Opportunity(
                title=analysis.get("title", "Untitled Opportunity"),
                content=content,
                category=analysis.get("category", "general"),
                deadline=analysis.get("deadline"),
                requirements=analysis.get("requirements", []),
                contact_info=analysis.get("contact_info"),
                priority_score=analysis.get("priority_score", 5),
                status="new",
                source="whatsapp"
            )
            
            db.add(opportunity)
            db.commit()
            
            # Send confirmation message
            confirmation = f"""
✅ Opportunity saved successfully!

📋 Title: {analysis.get('title', 'Untitled')}
🏷️ Category: {analysis.get('category', 'General')}
⏰ Deadline: {analysis.get('deadline', 'Not specified')}
⭐ Priority: {analysis.get('priority_score', 5)}/10

You can view all opportunities in your dashboard.
            """
            
            response.message(confirmation.strip())
        else:
            response.message("Hi! Send me any opportunity details and I'll analyze and save them for you. 📊")
            
    except Exception as e:
        response.message("Sorry, there was an error processing your message. Please try again.")
    
    return str(response)

async def process_media(media_url: str) -> str:
    """Process media files (images, PDFs) and extract text"""
    try:
        import requests
        from PIL import Image
        import pytesseract
        import io
        
        # Download the media
        response = requests.get(media_url)
        
        if response.headers.get('content-type', '').startswith('image/'):
            # Process image with OCR
            image = Image.open(io.BytesIO(response.content))
            text = pytesseract.image_to_string(image)
            return text
        else:
            return "Media file received but text extraction not supported for this format."
            
    except Exception as e:
        return "Error processing media file."

@whatsapp_router.get("/status")
async def webhook_status():
    return {"status": "WhatsApp webhook is running"}