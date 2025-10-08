# OpportunityBot Setup Guide

## Step 1: Environment Setup
```bash
# Copy environment file
copy .env.example .env
```

## Step 2: Configure API Keys
Edit `.env` file and add your keys:
```
OPENAI_API_KEY=sk-your-openai-key-here
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
WHATSAPP_PHONE_NUMBER=+1234567890
DATABASE_URL=sqlite:///./opportunities.db
```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Setup Database
```bash
python -c "from backend.models.opportunity import Base; from backend.database.connection import engine; Base.metadata.create_all(bind=engine); print('Database created!')"
```

## Step 5: Start Backend
```bash
cd backend
python main.py
```

## Step 6: Setup Dashboard (New Terminal)
```bash
cd dashboard
npm install
npm run dev
```

## Step 7: Test WhatsApp Integration
1. Go to Twilio Console
2. Set webhook URL: `https://your-domain.com/whatsapp/webhook`
3. Send test message to your WhatsApp number

## Access Points
- Dashboard: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs