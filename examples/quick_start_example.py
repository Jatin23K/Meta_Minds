#!/usr/bin/env python3
# =========================================================
# quick_start_example.py: Meta Minds Quick Start Example
# =========================================================
# Demonstrates how to use the Meta Minds ecosystem

import sys
import os
import asyncio
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent.parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

async def main():
    """Quick start example for Meta Minds."""
    
    print("🌟 Meta Minds Quick Start Example 🌟\n")
    
    # Example 1: Basic SMART Analysis
    print("📊 Example 1: Basic SMART Analysis")
    try:
        from core.smart_question_generator import SMARTQuestionGenerator, DatasetContext
        import pandas as pd
        
        # Create sample data
        sample_data = {
            'revenue': [100000, 120000, 110000, 130000, 125000],
            'profit': [20000, 25000, 22000, 28000, 26000],
            'customers': [500, 550, 525, 580, 570],
            'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Create context
        context = DatasetContext(
            subject_area="financial_analysis",
            target_audience="executives",
            business_objectives=["Understand revenue trends", "Assess profitability"]
        )
        
        # Generate questions
        generator = SMARTQuestionGenerator()
        questions = generator.generate_enhanced_questions(
            dataset_name="Monthly Financial Data",
            df=df,
            context=context,
            num_questions=5
        )
        
        print("✅ Generated SMART questions:")
        for i, q in enumerate(questions, 1):
            print(f"   {i}. {q}")
        print()
        
    except Exception as e:
        print(f"❌ Error in Example 1: {e}\n")
    
    # Example 2: Autonomous AI Agent Analysis
    print("🤖 Example 2: Autonomous AI Agent Analysis")
    try:
        from agents.autonomous_ai_agents import agent_manager, create_analysis_request
        
        # Create analysis request
        request = create_analysis_request(
            dataset_path="sample_data.csv",  # Would be actual file path
            domain="finance",
            analysis_type="comprehensive_analysis",
            objectives=["Revenue analysis", "Risk assessment"],
            priority="medium"
        )
        
        print(f"✅ Created analysis request: {request.request_id}")
        print(f"   Domain: {request.domain}")
        print(f"   Type: {request.analysis_type}")
        print(f"   Objectives: {', '.join(request.objectives)}")
        
        # Get agent status
        status = agent_manager.get_agent_performance_summary()
        print(f"   Available agents: {status['total_agents']}")
        print()
        
    except Exception as e:
        print(f"❌ Error in Example 2: {e}\n")
    
    # Example 3: Enterprise Integration
    print("🏢 Example 3: Enterprise Integration Setup")
    try:
        from integrations.enterprise_integrations import IntegrationConfig, setup_enterprise_integrations
        
        # Example configuration (would use real credentials)
        configs = [
            IntegrationConfig(
                platform="slack",
                credentials={"bot_token": "demo-token"},
                endpoints={},
                settings={"default_channel": "#analytics"}
            )
        ]
        
        print("✅ Enterprise integration configuration created")
        print("   Platform: Slack")
        print("   Settings: Default channel configured")
        print("   Note: Use real credentials for actual deployment")
        print()
        
    except Exception as e:
        print(f"❌ Error in Example 3: {e}\n")
    
    # Example 4: Workflow Creation
    print("🔄 Example 4: Workflow Management")
    try:
        from workflows.workflow_engine import workflow_engine
        
        # List available workflows
        workflows = workflow_engine.list_workflows()
        print(f"✅ Available workflows: {len(workflows)}")
        
        for workflow in workflows:
            print(f"   - {workflow['name']} ({workflow['steps_count']} steps)")
        
        if not workflows:
            print("   Note: Load workflow definitions from workflows/ directory")
        print()
        
    except Exception as e:
        print(f"❌ Error in Example 4: {e}\n")
    
    # Example 5: Real-time Collaboration
    print("🔄 Example 5: Real-time Collaboration")
    try:
        from integrations.realtime_collaboration import collaboration_manager
        
        # Create collaboration session
        session_id = await collaboration_manager.create_session(
            host_user_id="demo_user",
            name="Demo Analysis Session",
            description="Quick start demonstration"
        )
        
        print(f"✅ Created collaboration session: {session_id}")
        print("   Host: demo_user")
        print("   Name: Demo Analysis Session")
        print("   Note: Real sessions would support multiple users")
        print()
        
    except Exception as e:
        print(f"❌ Error in Example 5: {e}\n")
    
    print("🎉 Quick Start Examples Complete!")
    print("\n📚 Next Steps:")
    print("1. Run 'python launch.py' to start the full ecosystem")
    print("2. Access the web interface at http://localhost:8502")
    print("3. Upload your own datasets for analysis")
    print("4. Configure enterprise integrations with real credentials")
    print("5. Create custom workflows for your use cases")
    print("\n🌟 Enjoy using Meta Minds! 🌟")

if __name__ == "__main__":
    asyncio.run(main())
