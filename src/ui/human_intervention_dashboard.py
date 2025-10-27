# =========================================================
# human_intervention_dashboard.py: Human Oversight Dashboard
# =========================================================
# Web dashboard for managing human interventions across automation systems

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from automation_ecosystem import orchestrator, AutomationStatus, InterventionType, Priority

# Configure page
st.set_page_config(
    page_title="Automation Oversight Dashboard",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .intervention-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
    }
    
    .high-priority {
        border-left-color: #ef4444 !important;
    }
    
    .medium-priority {
        border-left-color: #f59e0b !important;
    }
    
    .low-priority {
        border-left-color: #10b981 !important;
    }
    
    .system-status-healthy {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
    
    .system-status-unhealthy {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class HumanInterventionDashboard:
    """Dashboard for managing human interventions."""
    
    def __init__(self):
        self.orchestrator = orchestrator
    
    def render_header(self):
        """Render dashboard header."""
        st.markdown("# 🎛️ Automation Oversight Dashboard")
        st.markdown("**Central control for all automation systems and human interventions**")
        
        # System overview metrics
        status = self.orchestrator.get_system_status()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Active Systems", status['registered_systems'])
        
        with col2:
            st.metric("Running Tasks", status['active_tasks'])
        
        with col3:
            pending = status['pending_interventions']
            st.metric("Pending Interventions", pending, 
                     delta=f"+{pending}" if pending > 0 else None)
        
        with col4:
            st.metric("Completed Tasks", status['completed_tasks'])
        
        with col5:
            healthy_systems = sum(1 for health in status['system_health'].values() if health)
            st.metric("Healthy Systems", f"{healthy_systems}/{status['registered_systems']}")
        
        st.markdown("---")
    
    def render_intervention_queue(self):
        """Render pending human interventions."""
        st.markdown("## 🚨 Pending Human Interventions")
        
        pending = self.orchestrator.pending_interventions
        
        if not pending:
            st.success("✅ No pending interventions - all systems running smoothly!")
            return
        
        # Sort by priority and creation time
        sorted_interventions = sorted(
            pending.values(),
            key=lambda x: (x.priority.value, x.created_at),
            reverse=True
        )
        
        for intervention in sorted_interventions:
            self._render_intervention_card(intervention)
    
    def _render_intervention_card(self, intervention):
        """Render individual intervention card."""
        priority_class = f"{intervention.priority.name.lower()}-priority"
        
        with st.container():
            st.markdown(f'<div class="intervention-card {priority_class}">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {intervention.title}")
                st.markdown(f"**Type:** {intervention.intervention_type.value.replace('_', ' ').title()}")
                st.markdown(f"**Description:** {intervention.description}")
                
                # Show context if available
                if intervention.context:
                    with st.expander("📋 Context Details"):
                        st.json(intervention.context)
            
            with col2:
                st.markdown(f"**Priority:** {intervention.priority.name}")
                st.markdown(f"**System:** {intervention.automation_id}")
                
                if intervention.deadline:
                    time_left = intervention.deadline - datetime.now()
                    if time_left.total_seconds() > 0:
                        st.markdown(f"**Deadline:** {time_left.days}d {time_left.seconds//3600}h")
                    else:
                        st.error("⏰ OVERDUE")
            
            with col3:
                st.markdown("**Actions:**")
                
                # Show available options
                if intervention.options:
                    selected_option = st.selectbox(
                        "Choose action:",
                        options=[opt['id'] for opt in intervention.options],
                        format_func=lambda x: next(opt['label'] for opt in intervention.options if opt['id'] == x),
                        key=f"option_{intervention.request_id}"
                    )
                    
                    if st.button(f"✅ Execute", key=f"execute_{intervention.request_id}"):
                        self._resolve_intervention(intervention.request_id, selected_option)
                        st.rerun()
                else:
                    # Generic resolution options
                    action = st.selectbox(
                        "Action:",
                        ["continue", "abort", "retry", "manual_review"],
                        key=f"action_{intervention.request_id}"
                    )
                    
                    if st.button(f"✅ Resolve", key=f"resolve_{intervention.request_id}"):
                        self._resolve_intervention(intervention.request_id, action)
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def _resolve_intervention(self, request_id: str, decision: str):
        """Resolve an intervention."""
        resolution = {
            "decision": decision,
            "resolved_at": datetime.now().isoformat(),
            "output": {"decision": decision}
        }
        
        success = self.orchestrator.resolve_intervention(
            request_id, resolution, "Human Operator"
        )
        
        if success:
            st.success(f"✅ Intervention resolved: {decision}")
        else:
            st.error("❌ Failed to resolve intervention")
    
    def render_system_status(self):
        """Render automation system status."""
        st.markdown("## 🖥️ Automation Systems Status")
        
        systems_data = []
        for system_id, system in self.orchestrator.systems.items():
            health = self.orchestrator.system_health.get(system_id, False)
            load = self.orchestrator._get_system_load(system_id)
            
            systems_data.append({
                "System": system.name,
                "ID": system_id,
                "Status": "🟢 Healthy" if health else "🔴 Unhealthy",
                "Load": f"{load}/{system.max_concurrent_tasks}",
                "Capabilities": ", ".join(system.capabilities[:3])
            })
        
        if systems_data:
            df = pd.DataFrame(systems_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No automation systems registered")
    
    def render_task_monitoring(self):
        """Render active task monitoring."""
        st.markdown("## 📋 Active Tasks")
        
        active_tasks = self.orchestrator.active_tasks
        
        if not active_tasks:
            st.info("No active tasks")
            return
        
        # Create tasks dataframe
        tasks_data = []
        for task in active_tasks.values():
            duration = ""
            if task.started_at:
                duration = str(datetime.now() - task.started_at).split('.')[0]
            
            tasks_data.append({
                "Task ID": task.task_id[:8],
                "Description": task.description,
                "System": task.automation_id,
                "Status": task.status.value.title(),
                "Priority": task.priority.name,
                "Duration": duration,
                "Needs Intervention": "Yes" if task.human_intervention else "No"
            })
        
        df = pd.DataFrame(tasks_data)
        st.dataframe(df, use_container_width=True)
        
        # Task status visualization
        status_counts = {}
        for task in active_tasks.values():
            status = task.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Task Status Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def render_analytics(self):
        """Render analytics and insights."""
        st.markdown("## 📊 Analytics & Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Intervention frequency over time
            st.markdown("### Intervention Frequency")
            
            # Simulated data for demo
            dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
            interventions = [abs(int(x)) for x in (2 + 1.5 * pd.Series(range(30)).apply(lambda x: x % 7 - 3) + 
                                                  pd.Series(range(30)).apply(lambda x: 0.5 * (x % 3 - 1)))]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=interventions,
                mode='lines+markers',
                name='Daily Interventions',
                line=dict(color='#ef4444')
            ))
            
            fig.update_layout(
                title="Human Interventions Over Time",
                xaxis_title="Date",
                yaxis_title="Number of Interventions"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # System reliability
            st.markdown("### System Reliability")
            
            # Simulated reliability data
            system_reliability = {
                "Meta Minds": 95.2,
                "Data Processor": 87.8,
                "File Manager": 92.1,
                "Email Automation": 98.5
            }
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(system_reliability.keys()),
                    y=list(system_reliability.values()),
                    marker_color=['#10b981' if v > 90 else '#f59e0b' if v > 80 else '#ef4444' 
                                 for v in system_reliability.values()]
                )
            ])
            
            fig.update_layout(
                title="System Reliability (%)",
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def render_workflow_builder(self):
        """Render workflow builder interface."""
        st.markdown("## 🔄 Workflow Builder")
        
        st.info("🚧 Workflow Builder - Build complex automation chains")
        
        with st.expander("Create New Workflow"):
            workflow_name = st.text_input("Workflow Name")
            workflow_description = st.text_area("Description")
            
            st.markdown("### Workflow Steps")
            
            # Simple workflow builder
            num_steps = st.number_input("Number of steps", min_value=1, max_value=10, value=3)
            
            workflow_steps = []
            for i in range(num_steps):
                st.markdown(f"#### Step {i+1}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    system = st.selectbox(
                        "Automation System",
                        options=list(self.orchestrator.systems.keys()),
                        key=f"system_{i}"
                    )
                
                with col2:
                    task_type = st.selectbox(
                        "Task Type",
                        options=["data_analysis", "file_processing", "notification", "validation"],
                        key=f"task_type_{i}"
                    )
                
                with col3:
                    priority = st.selectbox(
                        "Priority",
                        options=["LOW", "MEDIUM", "HIGH"],
                        key=f"priority_{i}"
                    )
                
                workflow_steps.append({
                    "step": i+1,
                    "system": system,
                    "task_type": task_type,
                    "priority": priority
                })
            
            if st.button("💾 Save Workflow"):
                workflow = {
                    "name": workflow_name,
                    "description": workflow_description,
                    "steps": workflow_steps,
                    "created_at": datetime.now().isoformat()
                }
                
                # Save workflow (in real implementation, save to database)
                st.success(f"✅ Workflow '{workflow_name}' saved!")
                st.json(workflow)
    
    def run(self):
        """Run the dashboard."""
        self.render_header()
        
        # Main content tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🚨 Interventions",
            "🖥️ Systems",
            "📋 Tasks",
            "📊 Analytics",
            "🔄 Workflows"
        ])
        
        with tab1:
            self.render_intervention_queue()
        
        with tab2:
            self.render_system_status()
        
        with tab3:
            self.render_task_monitoring()
        
        with tab4:
            self.render_analytics()
        
        with tab5:
            self.render_workflow_builder()

def main():
    """Main function to run the intervention dashboard."""
    dashboard = HumanInterventionDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
