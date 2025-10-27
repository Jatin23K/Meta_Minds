#!/usr/bin/env python3
"""
🧠 META MINDS - MAIN LAUNCHER
============================
Single entry point to run the entire Meta Minds application.

Usage:
    python main.py

This script will:
- Check and set up environment variables
- Verify dependencies
- Launch the Meta Minds application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# ANSI color codes for better output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    """Print the Meta Minds banner"""
    banner = f"""
{Colors.HEADER}╔══════════════════════════════════════════════════════════════╗
║                    🧠 META MINDS LAUNCHER                    ║
║                 AI-Powered Data Analysis Suite               ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    print(f"{Colors.OKBLUE}🔍 Checking Python version...{Colors.ENDC}")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{Colors.FAIL}❌ Python 3.8+ required. Current: {version.major}.{version.minor}{Colors.ENDC}")
        return False
    print(f"{Colors.OKGREEN}✅ Python {version.major}.{version.minor}.{version.micro} - Compatible{Colors.ENDC}")
    return True

def check_api_key():
    """Check and set up OpenAI API key"""
    print(f"{Colors.OKBLUE}🔑 Checking OpenAI API key...{Colors.ENDC}")
    
    # Check environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Check .env file
    env_file = Path(".env")
    if not api_key and env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('OPENAI_API_KEY='):
                        api_key = line.strip().split('=', 1)[1].strip('"\'')
                        os.environ["OPENAI_API_KEY"] = api_key
                        break
        except Exception as e:
            print(f"{Colors.WARNING}⚠️  Could not read .env file: {e}{Colors.ENDC}")
    
    if not api_key or api_key.startswith("sk-xxxx"):
        print(f"{Colors.WARNING}⚠️  OpenAI API key not found or is placeholder{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Please set your OpenAI API key:{Colors.ENDC}")
        print(f"1. Create a .env file with: OPENAI_API_KEY=your_key_here")
        print(f"2. Or set environment variable: export OPENAI_API_KEY=your_key_here")
        print(f"3. Get your key from: https://platform.openai.com/account/api-keys")
        
        # Prompt for API key
        try:
            user_key = input(f"\n{Colors.OKBLUE}Enter your OpenAI API key (or press Enter to skip): {Colors.ENDC}").strip()
            if user_key and user_key.startswith("sk-"):
                os.environ["OPENAI_API_KEY"] = user_key
                # Save to .env file
                with open(".env", "w") as f:
                    f.write(f"OPENAI_API_KEY={user_key}\n")
                print(f"{Colors.OKGREEN}✅ API key saved to .env file{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.WARNING}⚠️  Running without API key - some features may not work{Colors.ENDC}")
                return False
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Setup cancelled{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.OKGREEN}✅ API key found (ends with: ...{api_key[-8:]}){Colors.ENDC}")
        return True

def check_dependencies():
    """Check if required packages are installed"""
    print(f"{Colors.OKBLUE}📦 Checking dependencies...{Colors.ENDC}")
    
    required_packages = [
        "pandas", "numpy", "openai", "crewai", "streamlit"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"{Colors.WARNING}⚠️  Missing packages: {', '.join(missing_packages)}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}Installing missing packages...{Colors.ENDC}")
        
        try:
            # Try to install missing packages
            for package in missing_packages:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{Colors.OKGREEN}✅ All dependencies installed{Colors.ENDC}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}❌ Failed to install dependencies: {e}{Colors.ENDC}")
            print(f"{Colors.OKBLUE}Please run manually: pip install -r requirements.txt{Colors.ENDC}")
            return False
    else:
        print(f"{Colors.OKGREEN}✅ All dependencies found{Colors.ENDC}")
        return True

def launch_application():
    """Launch the Meta Minds application"""
    print(f"{Colors.OKBLUE}🚀 Launching Meta Minds...{Colors.ENDC}")
    
    # Change to source directory
    src_path = Path("src/core/main.py")
    if not src_path.exists():
        print(f"{Colors.FAIL}❌ Main application file not found: {src_path}{Colors.ENDC}")
        return False
    
    try:
        # Launch the main application
        subprocess.run([sys.executable, str(src_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}❌ Application failed to run: {e}{Colors.ENDC}")
        return False
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Application interrupted by user{Colors.ENDC}")
        return True

def show_help():
    """Show help information"""
    help_text = f"""
{Colors.OKBLUE}🧠 META MINDS - Usage Guide{Colors.ENDC}

{Colors.BOLD}Quick Start:{Colors.ENDC}
  python main.py                    # Run Meta Minds

{Colors.BOLD}Alternative Interfaces:{Colors.ENDC}
  streamlit run src/ui/app.py       # Web interface (port 8501)
  python src/core/main.py           # Direct CLI interface

{Colors.BOLD}Requirements:{Colors.ENDC}
  - Python 3.8+
  - OpenAI API key
  - Internet connection

{Colors.BOLD}Configuration:{Colors.ENDC}
  Create .env file with:
    OPENAI_API_KEY=your_key_here

{Colors.BOLD}Data Formats Supported:{Colors.ENDC}
  - CSV files
  - Excel files (.xlsx)
  - JSON files

{Colors.BOLD}Analysis Modes:{Colors.ENDC}
  1. SMART Enhanced Analysis (Recommended)
     - Context-aware question generation
     - Quality validation and scoring
     - Business context integration
  
  2. Standard Analysis
     - Basic dataset analysis
     - Fast processing
"""
    print(help_text)

def main():
    """Main launcher function"""
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            show_help()
            return
        elif sys.argv[1] in ["-v", "--version", "version"]:
            print("Meta Minds v1.0.0 - AI-Powered Data Analysis Suite")
            return
    
    print_banner()
    
    # System checks
    if not check_python_version():
        sys.exit(1)
    
    print()  # Add spacing
    
    # API key setup
    api_key_ok = check_api_key()
    print()  # Add spacing
    
    # Dependencies check
    if not check_dependencies():
        sys.exit(1)
    
    print()  # Add spacing
    
    # Launch application
    print(f"{Colors.OKGREEN}🎯 All checks passed! Starting Meta Minds...{Colors.ENDC}")
    print("-" * 60)
    
    if not launch_application():
        sys.exit(1)
    
    print(f"\n{Colors.OKGREEN}✅ Meta Minds session completed{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}🛑 Launcher interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
