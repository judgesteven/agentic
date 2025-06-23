#!/usr/bin/env python3
"""
Setup script for Agentic AI deployment to Vercel.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git():
    """Check if git is installed and repository is initialized."""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git is installed")
            return True
        else:
            print("❌ Git is not installed")
            return False
    except FileNotFoundError:
        print("❌ Git is not installed")
        return False

def check_vercel_cli():
    """Check if Vercel CLI is installed."""
    try:
        result = subprocess.run(['vercel', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Vercel CLI is installed")
            return True
        else:
            print("⚠️  Vercel CLI is not installed (optional)")
            return False
    except FileNotFoundError:
        print("⚠️  Vercel CLI is not installed (optional)")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import flask
        import requests
        print("✅ Required Python dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def create_env_file():
    """Create a .env file with example environment variables."""
    env_file = Path('.env')
    if not env_file.exists():
        env_content = """# Agentic AI Environment Variables
# Copy this file to .env and fill in your actual values

# OpenAI API Key (optional for demo mode)
OPENAI_API_KEY=your_openai_api_key_here

# Web Search API (optional)
SERPER_API_KEY=your_serper_api_key_here

# Weather API (optional)
WEATHER_API_KEY=your_weather_api_key_here

# Agent Configuration
AGENT_NAME=Agentic AI Assistant
AGENT_DESCRIPTION=Your intelligent AI assistant
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file with example variables")
    else:
        print("✅ .env file already exists")

def check_project_structure():
    """Check if the project structure is correct."""
    required_files = [
        'web_interface.py',
        'requirements.txt',
        'vercel.json',
        'api/index.py',
        'templates/index.html',
        '.github/workflows/deploy.yml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files are present")
        return True

def main():
    """Main setup function."""
    print("🚀 Agentic AI Deployment Setup")
    print("=" * 40)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    git_ok = check_git()
    vercel_ok = check_vercel_cli()
    deps_ok = check_dependencies()
    structure_ok = check_project_structure()
    
    # Create environment file
    print("\n🔧 Setting up environment...")
    create_env_file()
    
    # Summary
    print("\n📊 Setup Summary:")
    print(f"Git: {'✅' if git_ok else '❌'}")
    print(f"Vercel CLI: {'✅' if vercel_ok else '⚠️'}")
    print(f"Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"Project Structure: {'✅' if structure_ok else '❌'}")
    
    if not all([git_ok, deps_ok, structure_ok]):
        print("\n❌ Some prerequisites are missing. Please fix them before deploying.")
        sys.exit(1)
    
    print("\n🎉 Setup complete! Next steps:")
    print("1. Configure your .env file with actual API keys")
    print("2. Push your code to GitHub")
    print("3. Connect your repository to Vercel")
    print("4. Set up GitHub Secrets for automated deployment")
    print("\n📖 See DEPLOYMENT.md for detailed instructions")

if __name__ == '__main__':
    main() 