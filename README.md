# OpportunityBot - AI-Powered Opportunity Tracking System

## Overview
A comprehensive system to track, analyze, and manage opportunities through WhatsApp integration with an intelligent dashboard.

## System Architecture

### Components
1. **WhatsApp Bot** (`/whatsapp-bot/`)
   - Twilio/WhatsApp Business API integration
   - Message processing and routing
   - Media handling (images, PDFs, documents)

2. **AI Analysis Engine** (`/ai-engine/`)
   - OpenAI GPT integration for text analysis
   - OCR for image/document processing
   - NLP for requirement extraction
   - Classification and scoring algorithms

3. **Backend API** (`/backend/`)
   - FastAPI/Flask REST API
   - Database operations
   - Authentication and authorization
   - Notification services

4. **Dashboard Frontend** (`/dashboard/`)
   - React/Next.js web application
   - Responsive design
   - Real-time updates
   - Data visualization

5. **Database** (`/database/`)
   - PostgreSQL/MongoDB schemas
   - Migration scripts
   - Seed data

## Features

### WhatsApp Bot Features
- ✅ Process text opportunities
- ✅ Handle image/PDF uploads
- ✅ Extract key information automatically
- ✅ Classify opportunity types
- ✅ Set deadline reminders
- ✅ Confirmation messages with extracted data

### Dashboard Features
- ✅ Opportunity pipeline view
- ✅ Calendar integration
- ✅ Advanced filtering and search
- ✅ Analytics and reporting
- ✅ Export functionality
- ✅ Mobile responsive design

### AI Analysis Features
- ✅ OCR text extraction
- ✅ Deadline detection
- ✅ Requirement analysis
- ✅ Contact information extraction
- ✅ Priority scoring
- ✅ Category classification

## Tech Stack
- **Backend**: Python (FastAPI)
- **Frontend**: React/Next.js
- **Database**: PostgreSQL
- **AI**: OpenAI GPT-4, Tesseract OCR
- **WhatsApp**: Twilio WhatsApp API
- **Deployment**: Docker, AWS/Vercel

## Quick Start
```bash
# Clone and setup
git clone <repo>
cd ochatbot

# Install dependencies
pip install -r requirements.txt
npm install

# Setup environment
cp .env.example .env
# Configure your API keys

# Run development servers
python backend/main.py
npm run dev
```

## Environment Variables
```
OPENAI_API_KEY=your_openai_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
DATABASE_URL=your_database_url
WHATSAPP_PHONE_NUMBER=your_whatsapp_number
```