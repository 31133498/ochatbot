#!/usr/bin/env python3
"""
OpportunityBot Setup Script
Automates the initial setup process
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def setup_environment():
    """Setup environment variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        result = subprocess.run("copy .env.example .env", shell=True)
        if result.returncode == 0:
            print("⚠️  Please update .env file with your API keys before running the application")
            return True
        return False
    else:
        print("✅ .env file already exists")
        return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    return run_command("pip install -r requirements.txt")

def install_node_dependencies():
    """Install Node.js dependencies for dashboard"""
    print("📦 Installing Node.js dependencies...")
    return run_command("npm install", cwd="dashboard")

def setup_database():
    """Setup database tables"""
    print("🗄️ Setting up database...")
    # Create database tables
    setup_script = """
from backend.models.opportunity import Base
from backend.database.connection import engine
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")
"""
    
    with open("temp_setup_db.py", "w") as f:
        f.write(setup_script)
    
    success = run_command("python temp_setup_db.py")
    os.remove("temp_setup_db.py")
    return success

def main():
    """Main setup function"""
    print("🚀 Setting up OpportunityBot...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    steps = [
        ("Environment Setup", setup_environment),
        ("Python Dependencies", install_python_dependencies),
        ("Node.js Dependencies", install_node_dependencies),
        ("Database Setup", setup_database),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your API keys")
    print("2. Run: python backend/main.py (for API)")
    print("3. Run: cd dashboard && npm run dev (for dashboard)")
    print("4. Setup WhatsApp webhook URL in Twilio console")
    print("\n🔗 Dashboard: http://localhost:3000")
    print("🔗 API: http://localhost:8000")

if __name__ == "__main__":
    main()