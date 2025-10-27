# =========================================================
# automation_ecosystem.py: Central Automation Ecosystem
# =========================================================
# Orchestrates multiple automation systems including Meta Minds
# Handles inter-system communication and human intervention requests

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import threading
import queue
import websockets

class AutomationStatus(Enum):
    """Status of automation tasks."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_HUMAN = "waiting_human"
    PAUSED = "paused"

class Priority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class InterventionType(Enum):
    """Types of human intervention needed."""
    DECISION_REQUIRED = "decision_required"
    DATA_VALIDATION = "data_validation"
    APPROVAL_NEEDED = "approval_needed"
    ERROR_RESOLUTION = "error_resolution"
    QUALITY_REVIEW = "quality_review"
    CONTEXT_CLARIFICATION = "context_clarification"

@dataclass
class HumanInterventionRequest:
    """Request for human intervention."""
    request_id: str
    automation_id: str
    intervention_type: InterventionType
    priority: Priority
    title: str
    description: str
    context: Dict[str, Any]
    options: List[Dict[str, Any]]  # Available choices for human
    deadline: Optional[datetime]
    callback_function: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution: Optional[Dict[str, Any]] = None
    resolved_by: Optional[str] = None

@dataclass
class AutomationTask:
    """Individual automation task."""
    task_id: str
    automation_id: str
    task_type: str
    description: str
    priority: Priority
    status: AutomationStatus
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    dependencies: List[str] = None  # Other task IDs this depends on
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    human_intervention: Optional[HumanInterventionRequest] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class AutomationSystem:
    """Definition of an automation system."""
    system_id: str
    name: str
    description: str
    capabilities: List[str]
    input_types: List[str]
    output_types: List[str]
    endpoint: str
    health_check_url: str
    max_concurrent_tasks: int = 5
    timeout_seconds: int = 300
    requires_human_oversight: bool = False

class AutomationOrchestrator:
    """Central orchestrator for all automation systems."""
    
    def __init__(self, config_file: str = "automation_config.json"):
        self.systems: Dict[str, AutomationSystem] = {}
        self.active_tasks: Dict[str, AutomationTask] = {}
        self.pending_interventions: Dict[str, HumanInterventionRequest] = {}
        self.completed_tasks: List[AutomationTask] = []
        self.shared_context: Dict[str, Any] = {}
        
        # Communication channels
        self.task_queue = asyncio.Queue()
        self.intervention_queue = queue.Queue()
        self.system_health: Dict[str, bool] = {}
        
        # Load configuration
        self.config_file = config_file
        self.load_configuration()
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("AutomationOrchestrator")
        
    def register_automation_system(self, system: AutomationSystem):
        """Register a new automation system."""
        self.systems[system.system_id] = system
        self.system_health[system.system_id] = False
        self.logger.info(f"Registered automation system: {system.name}")
        
    async def submit_task(self, task: AutomationTask) -> str:
        """Submit a task to the orchestrator."""
        self.active_tasks[task.task_id] = task
        await self.task_queue.put(task)
        self.logger.info(f"Task submitted: {task.task_id} - {task.description}")
        return task.task_id
    
    async def process_tasks(self):
        """Main task processing loop."""
        while True:
            try:
                # Get next task
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Check dependencies
                if not self._check_dependencies(task):
                    # Re-queue task if dependencies not met
                    await asyncio.sleep(5)
                    await self.task_queue.put(task)
                    continue
                
                # Find appropriate automation system
                system = self._find_suitable_system(task)
                if not system:
                    await self._request_human_intervention(
                        task, 
                        InterventionType.ERROR_RESOLUTION,
                        "No suitable automation system found",
                        {"available_systems": list(self.systems.keys())}
                    )
                    continue
                
                # Execute task
                await self._execute_task(task, system)
                
            except asyncio.TimeoutError:
                # No tasks available, continue
                continue
            except Exception as e:
                self.logger.error(f"Error in task processing: {e}")
    
    def _check_dependencies(self, task: AutomationTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id in self.active_tasks:
                dep_task = self.active_tasks[dep_id]
                if dep_task.status != AutomationStatus.COMPLETED:
                    return False
        return True
    
    def _find_suitable_system(self, task: AutomationTask) -> Optional[AutomationSystem]:
        """Find the best automation system for a task."""
        suitable_systems = []
        
        for system in self.systems.values():
            # Check if system is healthy
            if not self.system_health.get(system.system_id, False):
                continue
                
            # Check if system can handle task type
            if task.task_type in system.capabilities:
                suitable_systems.append(system)
        
        if not suitable_systems:
            return None
            
        # Return system with lowest current load
        return min(suitable_systems, 
                  key=lambda s: self._get_system_load(s.system_id))
    
    def _get_system_load(self, system_id: str) -> int:
        """Get current load for a system."""
        return sum(1 for task in self.active_tasks.values() 
                  if task.automation_id == system_id and 
                  task.status == AutomationStatus.RUNNING)
    
    async def _execute_task(self, task: AutomationTask, system: AutomationSystem):
        """Execute a task on the specified system."""
        try:
            task.status = AutomationStatus.RUNNING
            task.started_at = datetime.now()
            task.automation_id = system.system_id
            
            # Call automation system
            result = await self._call_automation_system(system, task)
            
            # Handle different result types
            if result.get("requires_human_intervention"):
                await self._request_human_intervention(
                    task,
                    InterventionType.DECISION_REQUIRED,
                    result.get("intervention_reason", "Decision required"),
                    result.get("context", {}),
                    result.get("options", [])
                )
            elif result.get("success"):
                task.status = AutomationStatus.COMPLETED
                task.completed_at = datetime.now()
                task.output_data = result.get("output")
                self._move_to_completed(task)
            else:
                task.status = AutomationStatus.FAILED
                task.error_message = result.get("error", "Unknown error")
                
        except Exception as e:
            task.status = AutomationStatus.FAILED
            task.error_message = str(e)
            self.logger.error(f"Task execution failed: {e}")
    
    async def _call_automation_system(self, system: AutomationSystem, task: AutomationTask) -> Dict[str, Any]:
        """Call an automation system to execute a task."""
        # This would be implemented based on each system's API
        # For Meta Minds, it would call the SMART analysis functions
        
        if system.system_id == "meta_minds":
            return await self._call_meta_minds(task)
        elif system.system_id == "data_processor":
            return await self._call_data_processor(task)
        # Add other automation systems here
        
        return {"success": False, "error": "Unknown system"}
    
    async def _call_meta_minds(self, task: AutomationTask) -> Dict[str, Any]:
        """Call Meta Minds for data analysis tasks."""
        try:
            from smart_question_generator import SMARTQuestionGenerator, DatasetContext
            from smart_validator import SMARTValidator
            import pandas as pd
            
            # Extract task data
            dataset_path = task.input_data.get("dataset_path")
            context_config = task.input_data.get("context", {})
            
            if not dataset_path:
                return {
                    "success": False,
                    "requires_human_intervention": True,
                    "intervention_reason": "Dataset path not provided",
                    "context": {"task_id": task.task_id}
                }
            
            # Load dataset
            df = pd.read_csv(dataset_path)
            
            # Create context
            context = DatasetContext(**context_config)
            
            # Check if dataset is suitable for analysis
            if len(df) < 10:
                return {
                    "success": False,
                    "requires_human_intervention": True,
                    "intervention_reason": "Dataset too small for meaningful analysis",
                    "context": {"dataset_size": len(df)},
                    "options": [
                        {"id": "continue", "label": "Continue anyway"},
                        {"id": "abort", "label": "Abort analysis"},
                        {"id": "request_more_data", "label": "Request more data"}
                    ]
                }
            
            # Generate questions
            generator = SMARTQuestionGenerator()
            questions = generator.generate_enhanced_questions(
                dataset_name=task.input_data.get("dataset_name", "dataset"),
                df=df,
                context=context,
                num_questions=20
            )
            
            # Validate quality
            validator = SMARTValidator()
            quality_report = validator.validate_question_set(questions, context)
            
            # Check if quality meets standards
            avg_quality = quality_report['summary']['average_score']
            if avg_quality < 0.6:
                return {
                    "success": False,
                    "requires_human_intervention": True,
                    "intervention_reason": f"Question quality below threshold: {avg_quality:.2f}",
                    "context": {
                        "quality_score": avg_quality,
                        "questions": questions[:5]  # Show sample
                    },
                    "options": [
                        {"id": "accept", "label": "Accept current quality"},
                        {"id": "retry", "label": "Retry with different approach"},
                        {"id": "manual_review", "label": "Request manual review"}
                    ]
                }
            
            return {
                "success": True,
                "output": {
                    "questions": questions,
                    "quality_report": quality_report,
                    "analysis_summary": {
                        "dataset_size": len(df),
                        "avg_quality": avg_quality,
                        "high_quality_questions": quality_report['summary']['high_quality_count']
                    }
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "requires_human_intervention": True,
                "intervention_reason": "Meta Minds analysis failed",
                "context": {"error": str(e)}
            }
    
    async def _request_human_intervention(self, task: AutomationTask, 
                                        intervention_type: InterventionType,
                                        reason: str,
                                        context: Dict[str, Any],
                                        options: List[Dict[str, Any]] = None):
        """Request human intervention for a task."""
        
        intervention = HumanInterventionRequest(
            request_id=str(uuid.uuid4()),
            automation_id=task.automation_id,
            intervention_type=intervention_type,
            priority=task.priority,
            title=f"Human intervention needed: {task.description}",
            description=reason,
            context=context,
            options=options or [],
            deadline=datetime.now() + timedelta(hours=24),  # Default 24h deadline
            callback_function="resolve_intervention",
            created_at=datetime.now()
        )
        
        task.status = AutomationStatus.WAITING_HUMAN
        task.human_intervention = intervention
        self.pending_interventions[intervention.request_id] = intervention
        
        # Notify human operators
        await self._notify_human_operators(intervention)
        
        self.logger.info(f"Human intervention requested for task {task.task_id}: {reason}")
    
    async def _notify_human_operators(self, intervention: HumanInterventionRequest):
        """Notify human operators about intervention needed."""
        notification = {
            "type": "human_intervention_required",
            "request_id": intervention.request_id,
            "priority": intervention.priority.name,
            "title": intervention.title,
            "description": intervention.description,
            "deadline": intervention.deadline.isoformat() if intervention.deadline else None,
            "options": intervention.options
        }
        
        # Send via multiple channels
        await self._send_slack_notification(notification)
        await self._send_email_notification(notification)
        await self._send_dashboard_notification(notification)
    
    async def _send_slack_notification(self, notification: Dict[str, Any]):
        """Send notification via Slack."""
        # Implementation would integrate with Slack API
        self.logger.info(f"Slack notification sent: {notification['title']}")
    
    async def _send_email_notification(self, notification: Dict[str, Any]):
        """Send notification via email."""
        # Implementation would integrate with email service
        self.logger.info(f"Email notification sent: {notification['title']}")
    
    async def _send_dashboard_notification(self, notification: Dict[str, Any]):
        """Send notification to web dashboard."""
        # Implementation would update web dashboard
        self.logger.info(f"Dashboard notification sent: {notification['title']}")
    
    def resolve_intervention(self, request_id: str, resolution: Dict[str, Any], resolved_by: str):
        """Resolve a human intervention request."""
        if request_id not in self.pending_interventions:
            self.logger.error(f"Intervention request not found: {request_id}")
            return False
        
        intervention = self.pending_interventions[request_id]
        intervention.resolved_at = datetime.now()
        intervention.resolution = resolution
        intervention.resolved_by = resolved_by
        
        # Find associated task and continue processing
        task = None
        for t in self.active_tasks.values():
            if t.human_intervention and t.human_intervention.request_id == request_id:
                task = t
                break
        
        if task:
            # Process resolution and continue task
            asyncio.create_task(self._continue_task_after_intervention(task, resolution))
        
        # Remove from pending
        del self.pending_interventions[request_id]
        
        self.logger.info(f"Intervention resolved by {resolved_by}: {request_id}")
        return True
    
    async def _continue_task_after_intervention(self, task: AutomationTask, resolution: Dict[str, Any]):
        """Continue task execution after human intervention."""
        decision = resolution.get("decision")
        
        if decision == "abort":
            task.status = AutomationStatus.FAILED
            task.error_message = "Aborted by human intervention"
        elif decision == "retry":
            task.status = AutomationStatus.IDLE
            task.human_intervention = None
            await self.task_queue.put(task)  # Re-queue
        elif decision == "continue" or decision == "accept":
            task.status = AutomationStatus.COMPLETED
            task.completed_at = datetime.now()
            task.output_data = resolution.get("output", {})
            self._move_to_completed(task)
        elif decision == "manual_review":
            # Keep in waiting state for manual processing
            pass
    
    def _move_to_completed(self, task: AutomationTask):
        """Move task to completed list and update shared context."""
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]
        
        self.completed_tasks.append(task)
        
        # Update shared context with task results
        if task.output_data:
            self.shared_context[f"task_{task.task_id}"] = {
                "output": task.output_data,
                "completed_at": task.completed_at.isoformat(),
                "automation_system": task.automation_id
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "registered_systems": len(self.systems),
            "active_tasks": len(self.active_tasks),
            "pending_interventions": len(self.pending_interventions),
            "completed_tasks": len(self.completed_tasks),
            "system_health": self.system_health,
            "tasks_by_status": {
                status.value: sum(1 for t in self.active_tasks.values() if t.status == status)
                for status in AutomationStatus
            }
        }
    
    def load_configuration(self):
        """Load automation system configuration."""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            for system_config in config.get("systems", []):
                system = AutomationSystem(**system_config)
                self.register_automation_system(system)
    
    def save_configuration(self):
        """Save automation system configuration."""
        config = {
            "systems": [asdict(system) for system in self.systems.values()],
            "updated_at": datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

# Global orchestrator instance
orchestrator = AutomationOrchestrator()

# Register Meta Minds as an automation system
meta_minds_system = AutomationSystem(
    system_id="meta_minds",
    name="Meta Minds - SMART Data Analysis",
    description="AI-powered data analysis with SMART question generation",
    capabilities=["data_analysis", "question_generation", "quality_validation"],
    input_types=["csv", "excel", "json", "dataset"],
    output_types=["questions", "quality_report", "analysis_summary"],
    endpoint="http://localhost:8501/api",
    health_check_url="http://localhost:8501/health",
    max_concurrent_tasks=3,
    timeout_seconds=300,
    requires_human_oversight=True
)

orchestrator.register_automation_system(meta_minds_system)
