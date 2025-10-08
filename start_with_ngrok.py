"""
Start OpportunityBot with ngrok tunnel
"""
import subprocess
import time
import threading
import requests
import json

def start_ngrok():
    """Start ngrok tunnel"""
    try:
        # Start ngrok
        process = subprocess.Popen(['ngrok.exe', 'http', '8000'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get ngrok URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels')
            tunnels = response.json()['tunnels']
            if tunnels:
                public_url = tunnels[0]['public_url']
                print(f"🌐 Ngrok URL: {public_url}")
                print(f"📱 WhatsApp Webhook: {public_url}/whatsapp")
                return public_url
        except:
            print("⚠️ Could not get ngrok URL")
            
    except Exception as e:
        print(f"❌ Ngrok failed: {e}")
    
    return None

def start_bot():
    """Start the bot"""
    import uvicorn
    from final_bot import app
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    print("🚀 Starting OpportunityBot with ngrok...")
    
    # Start ngrok in background
    ngrok_thread = threading.Thread(target=start_ngrok)
    ngrok_thread.daemon = True
    ngrok_thread.start()
    
    # Wait a bit for ngrok
    time.sleep(5)
    
    # Start the bot
    print("🤖 Starting bot server...")
    start_bot()