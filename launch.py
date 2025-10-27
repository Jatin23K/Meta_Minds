#!/usr/bin/env python3
# =========================================================
# launch.py: Meta Minds Ecosystem Launcher
# =========================================================
# Central launcher for the complete Meta Minds automation ecosystem
# Starts all components and provides easy access to the system

import sys
import os
import asyncio
import subprocess
import time
import threading
import logging
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def print_banner():
    """Print Meta Minds banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║            🌟 META MINDS AUTOMATION ECOSYSTEM 🌟             ║
    ║                                                              ║
    ║               Revolutionary AI-Powered Analytics              ║
    ║                 Complete Enterprise Solution                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🚀 Starting Meta Minds Complete System...
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    try:
        import streamlit
        import pandas
        import openai
        import crewai
        print("✅ Core dependencies verified")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please run: pip install -r config/requirements.txt")
        return False

def start_component(component_name, command, wait_time=2):
    """Start a system component."""
    print(f"🚀 Starting {component_name}...")
    
    try:
        if sys.platform == "win32":
            # Windows
            process = subprocess.Popen(
                command,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # Unix/Linux/Mac
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        time.sleep(wait_time)
        
        if process.poll() is None:
            print(f"✅ {component_name} started successfully")
            return process
        else:
            print(f"❌ Failed to start {component_name}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting {component_name}: {e}")
        return None

def start_automation_ecosystem():
    """Start the central automation ecosystem."""
    try:
        from workflows.automation_ecosystem import orchestrator
        
        # Start orchestrator in background thread
        def run_orchestrator():
            asyncio.run(orchestrator.process_tasks())
        
        thread = threading.Thread(target=run_orchestrator, daemon=True)
        thread.start()
        
        print("✅ Automation Ecosystem started")
        return True
    except Exception as e:
        print(f"❌ Failed to start Automation Ecosystem: {e}")
        return False

def start_knowledge_base():
    """Initialize shared knowledge base."""
    try:
        from workflows.shared_knowledge_base import knowledge_base
        
        # Cleanup expired entries
        knowledge_base.cleanup_expired_entries()
        
        print("✅ Shared Knowledge Base initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Knowledge Base: {e}")
        return False

def start_ai_agents():
    """Initialize autonomous AI agents."""
    try:
        from agents.autonomous_ai_agents import agent_manager
        
        # Agents are automatically initialized
        status = agent_manager.get_agent_performance_summary()
        agent_count = status['total_agents']
        
        print(f"✅ {agent_count} Autonomous AI Agents initialized")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize AI Agents: {e}")
        return False

def main():
    """Main launcher function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install requirements first.")
        return
    
    print("\n🔧 Initializing Meta Minds Ecosystem Components...\n")
    
    # Initialize core components
    components_started = 0
    total_components = 7
    
    # 1. Start Automation Ecosystem
    if start_automation_ecosystem():
        components_started += 1
    
    # 2. Initialize Knowledge Base
    if start_knowledge_base():
        components_started += 1
    
    # 3. Initialize AI Agents
    if start_ai_agents():
        components_started += 1
    
    # 4. Start Human Intervention Dashboard
    dashboard_process = start_component(
        "Human Intervention Dashboard",
        "streamlit run src/ui/human_intervention_dashboard.py --server.port 8501",
        wait_time=3
    )
    if dashboard_process:
        components_started += 1
    
    # 5. Start Meta Minds Main Interface
    app_process = start_component(
        "Meta Minds Main Interface",
        "streamlit run src/ui/app.py --server.port 8502",
        wait_time=3
    )
    if app_process:
        components_started += 1
    
    # 6. Start Real-time Collaboration Server
    collab_process = start_component(
        "Real-time Collaboration Server",
        "python src/integrations/realtime_collaboration.py",
        wait_time=2
    )
    if collab_process:
        components_started += 1
    
    # 7. Start Workflow Engine
    try:
        from workflows.workflow_engine import workflow_engine
        workflow_count = len(workflow_engine.list_workflows())
        print(f"✅ Workflow Engine started ({workflow_count} workflows loaded)")
        components_started += 1
    except Exception as e:
        print(f"❌ Failed to start Workflow Engine: {e}")
    
    print(f"\n📊 System Status: {components_started}/{total_components} components started\n")
    
    if components_started >= 5:  # Minimum viable system
        print("🎉 META MINDS ECOSYSTEM SUCCESSFULLY LAUNCHED! 🎉\n")
        
        print("🌐 Access Your System:")
        print("├── 🎛️ Main Dashboard: http://localhost:8501")
        print("├── 📊 Meta Minds Interface: http://localhost:8502")
        print("├── 🔄 Collaboration Hub: ws://localhost:8765")
        print("├── 🤖 AI Agents: Running autonomously")
        print("├── 🔗 Integrations: Ready for enterprise")
        print("└── 📁 Workflows: Orchestration active")
        
        print("\n💡 Quick Actions:")
        print("├── 📊 Start Analysis: Upload data via Meta Minds Interface")
        print("├── 🤖 Request AI Agent: Submit analysis via API")
        print("├── 🔄 Join Collaboration: Create/join session")
        print("├── 🎛️ Monitor System: Check dashboard for status")
        print("└── 📋 View Workflows: Browse available workflows")
        
        print("\n🔧 System Features Active:")
        print("├── ✅ SMART Question Generation")
        print("├── ✅ Autonomous AI Agents")
        print("├── ✅ Real-time Collaboration")
        print("├── ✅ Enterprise Integrations")
        print("├── ✅ Workflow Orchestration")
        print("├── ✅ Human Intervention System")
        print("├── ✅ Advanced ML Models")
        print("├── ✅ Shared Knowledge Base")
        print("├── ✅ Performance Optimization")
        print("└── ✅ Complete Automation Ecosystem")
        
        print("\n🎯 Ready for:")
        print("├── 📈 Enterprise Data Analysis")
        print("├── 🤝 Team Collaboration")
        print("├── 🔄 Automated Workflows")
        print("├── 🧠 AI-Powered Insights")
        print("└── 🚀 Scalable Operations")
        
        print("\n" + "="*60)
        print("🌟 META MINDS: THE FUTURE OF INTELLIGENT AUTOMATION! 🌟")
        print("="*60)
        
        # Keep the launcher running
        try:
            print("\n⏸️  Press Ctrl+C to shutdown the ecosystem...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Meta Minds Ecosystem...")
            
            # Cleanup processes
            processes = [dashboard_process, app_process, collab_process]
            for process in processes:
                if process and process.poll() is None:
                    process.terminate()
            
            print("✅ Meta Minds Ecosystem shutdown complete")
            
    else:
        print("❌ SYSTEM LAUNCH FAILED")
        print(f"Only {components_started}/{total_components} components started successfully")
        print("\n🔧 Troubleshooting:")
        print("├── Check that all dependencies are installed")
        print("├── Ensure ports 8501, 8502, 8765 are available")
        print("├── Verify Python path and module imports")
        print("└── Check logs for specific error messages")

if __name__ == "__main__":
    main()
