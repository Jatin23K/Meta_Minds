#!/usr/bin/env python3
"""
🧠 META MINDS STANDALONE LAUNCHER
=================================
Launch Meta Minds as an independent application

This launcher provides access to the original Meta Minds Streamlit interface
for standalone usage without architectural dependencies.
"""

import subprocess
import sys
import time
import webbrowser
import os
from pathlib import Path

def print_banner():
    print("🧠" + "="*50 + "🧠")
    print("   META MINDS STANDALONE LAUNCHER")
    print("   🔓 Independent Mode")
    print("🧠" + "="*50 + "🧠")
    print()

def check_streamlit():
    """Check if streamlit is available"""
    try:
        # Try to find streamlit in the virtual environment
        venv_path = Path("venv/Scripts")
        if venv_path.exists():
            streamlit_exe = venv_path / "streamlit.exe"
            if streamlit_exe.exists():
                return str(streamlit_exe)
        
        # Try system streamlit
        result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return f"{sys.executable} -m streamlit"
            
    except Exception:
        pass
    
    return None

def activate_venv():
    """Activate the virtual environment"""
    venv_path = Path("venv")
    if venv_path.exists():
        if os.name == 'nt':  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            if activate_script.exists():
                return str(activate_script)
        else:  # Unix/Linux/Mac
            activate_script = venv_path / "bin" / "activate"
            if activate_script.exists():
                return str(activate_script)
    return None

def launch_streamlit_app():
    """Launch the original Meta Minds Streamlit interface"""
    print("🚀 LAUNCHING META MINDS STREAMLIT INTERFACE")
    print("=" * 45)
    print("🔗 URL: http://localhost:8502")
    print("💡 Features:")
    print("   • Original Meta Minds Interface")
    print("   • Enhanced Input Configuration")
    print("   • SMART Question Generation")
    print("   • Open-ended Question Validation")
    print("   • Standalone Operation")
    print()
    
    # Check if we're in the right directory
    app_file = Path("src/ui/app.py")
    if not app_file.exists():
        print("❌ Error: src/ui/app.py not found!")
        print("💡 Make sure you're running this from the META_MINDS_INDIVIDUAL folder")
        return False
    
    # Check for streamlit
    streamlit_cmd = check_streamlit()
    if not streamlit_cmd:
        print("⚠️  Streamlit not found. Attempting to install...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
            streamlit_cmd = f"{sys.executable} -m streamlit"
        except Exception as e:
            print(f"❌ Failed to install streamlit: {e}")
            return False
    
    try:
        # Prepare the command
        if "streamlit.exe" in streamlit_cmd:
            cmd = [streamlit_cmd, "run", str(app_file), "--server.port", "8502"]
        else:
            cmd = streamlit_cmd.split() + ["run", str(app_file), "--server.port", "8502"]
        
        print("🔄 Starting Streamlit server...")
        
        # Launch streamlit
        process = subprocess.Popen(cmd)
        
        # Wait a moment then open browser
        time.sleep(5)
        webbrowser.open("http://localhost:8502")
        
        print("✅ Meta Minds launched successfully!")
        print("🌐 Opening in your default browser...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error launching Meta Minds: {e}")
        return False

def main():
    print_banner()
    
    print("📋 STANDALONE META MINDS OPTIONS:")
    print("1. 🚀 Launch Meta Minds Streamlit Interface")
    print("2. 📖 View Documentation")
    print("3. ❌ Exit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        success = launch_streamlit_app()
        if success:
            print("\n🔄 Meta Minds is running...")
            print("💡 Press Ctrl+C to stop the service")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down Meta Minds...")
                print("✅ Service stopped. Goodbye!")
        
    elif choice == "2":
        print("📖 DOCUMENTATION LOCATIONS:")
        print("   • README.md - Main project documentation")
        print("   • docs/ - Detailed guides and documentation")
        print("   • PROJECT_STRUCTURE.md - Project organization")
        
    elif choice == "3":
        print("👋 Goodbye!")
        return
        
    else:
        print("❌ Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
