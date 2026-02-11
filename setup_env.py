#!/usr/bin/env python3
"""
Environment Setup Script for Advanced RAG System
Automatically sets up virtual environment, installs dependencies, and creates configuration files.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(command, description="", check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Python 3.11 or higher is required.")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def create_virtual_environment():
    """Create virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("📦 Creating virtual environment...")
    success = run_command(
        f"{sys.executable} -m venv venv",
        "Creating virtual environment"
    )
    
    if success:
        print("✅ Virtual environment created successfully")
        return True
    else:
        print("❌ Failed to create virtual environment")
        return False


def get_venv_python():
    """Get path to virtual environment Python executable."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")


def get_venv_pip():
    """Get path to virtual environment pip executable."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")


def install_dependencies():
    """Install project dependencies."""
    venv_pip = get_venv_pip()
    
    print("📚 Installing dependencies...")
    
    # Upgrade pip first
    run_command(
        f"{venv_pip} install --upgrade pip",
        "Upgrading pip"
    )
    
    # Install requirements
    success = run_command(
        f"{venv_pip} install -r requirements.txt",
        "Installing requirements"
    )
    
    if success:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print("❌ Failed to install dependencies")
        return False


def create_env_file():
    """Create .env file from template."""
    env_file = Path(".env")
    env_template = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📝 Creating .env file...")
    
    env_content = """# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Serper API Key (Required for web search)
SERPER_API_KEY=your_serper_api_key_here

# Ollama Configuration (Optional)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama-3.1-latest

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
EMBEDDING_MODEL=models/gemini-embedding-001

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        print("⚠️  Please update GOOGLE_API_KEY in .env file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "uploads", 
        "chroma_db",
        "logs",
        "temp"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"📁 Created directory: {directory}")
    
    print("✅ All directories created")


def test_installation():
    """Test if installation was successful."""
    venv_python = get_venv_python()
    
    print("🧪 Testing installation...")
    
    test_script = """
import sys
sys.path.insert(0, 'backend')

try:
    from agents.langchain_agents import create_query_analysis_agent
    from graph import build_rag_graph
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
"""
    
    success = run_command(
        f'{venv_python} -c "{test_script}"',
        "Testing core imports"
    )
    
    return success


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Update your .env file with your Google API key")
    print("2. Activate the virtual environment:")
    
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("3. Start the server:")
    print("   cd backend")
    print("   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    
    print("\n📚 API Documentation:")
    print("   http://localhost:8000/docs")
    
    print("\n🔍 Health Check:")
    print("   http://localhost:8000/health")
    
    print("\n📞 For issues, check the README.md file")


def main():
    """Main setup function."""
    print("🚀 Advanced RAG System - Environment Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Create directories
    create_directories()
    
    # Test installation
    if not test_installation():
        print("⚠️  Installation completed with warnings. Check the error messages above.")
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
