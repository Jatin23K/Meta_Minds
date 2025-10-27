# =========================================================
# workflow_engine.py: Advanced Workflow Orchestration Engine
# =========================================================
# Orchestrates complex workflows across multiple automation systems
# with conditional logic, loops, and intelligent decision making

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import yaml
from pathlib import Path

from automation_ecosystem import AutomationTask, AutomationStatus, Priority, orchestrator
from shared_knowledge_base import knowledge_base

class WorkflowStatus(Enum):
    """Workflow execution status."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepType(Enum):
    """Types of workflow steps."""
    TASK = "task"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    WAIT = "wait"
    HUMAN_INPUT = "human_input"
    DECISION = "decision"

class ConditionOperator(Enum):
    """Logical operators for conditions."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"

@dataclass
class WorkflowCondition:
    """Condition for workflow control flow."""
    variable: str
    operator: ConditionOperator
    value: Any
    source: str = "output"  # 'output', 'context', 'constant'

@dataclass
class WorkflowStep:
    """Individual step in a workflow."""
    step_id: str
    step_type: StepType
    name: str
    description: str
    
    # Task-specific properties
    automation_system: Optional[str] = None
    task_type: Optional[str] = None
    input_mapping: Dict[str, str] = None
    output_mapping: Dict[str, str] = None
    
    # Control flow properties
    condition: Optional[WorkflowCondition] = None
    next_step_success: Optional[str] = None
    next_step_failure: Optional[str] = None
    parallel_steps: List[str] = None
    loop_condition: Optional[WorkflowCondition] = None
    max_iterations: int = 10
    
    # Timing properties
    timeout_seconds: int = 300
    retry_count: int = 3
    retry_delay_seconds: int = 5
    
    # Human interaction
    human_prompt: Optional[str] = None
    human_options: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.input_mapping is None:
            self.input_mapping = {}
        if self.output_mapping is None:
            self.output_mapping = {}
        if self.parallel_steps is None:
            self.parallel_steps = []
        if self.human_options is None:
            self.human_options = []

@dataclass
class WorkflowDefinition:
    """Complete workflow definition."""
    workflow_id: str
    name: str
    description: str
    version: str
    created_by: str
    created_at: datetime
    
    steps: List[WorkflowStep]
    start_step: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    
    # Metadata
    tags: List[str] = None
    category: str = "general"
    estimated_duration_minutes: int = 30
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class WorkflowExecution:
    """Runtime execution of a workflow."""
    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str]
    
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    context: Dict[str, Any]
    step_outputs: Dict[str, Any]  # Output from each step
    
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # Execution tracking
    executed_steps: List[str] = None
    failed_steps: List[str] = None
    retry_counts: Dict[str, int] = None
    
    def __post_init__(self):
        if self.executed_steps is None:
            self.executed_steps = []
        if self.failed_steps is None:
            self.failed_steps = []
        if self.retry_counts is None:
            self.retry_counts = {}

class WorkflowEngine:
    """Advanced workflow orchestration engine."""
    
    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.execution_queue = asyncio.Queue()
        
        # Built-in functions for workflow steps
        self.built_in_functions = {
            "wait": self._wait_function,
            "log": self._log_function,
            "set_variable": self._set_variable_function,
            "send_notification": self._send_notification_function,
            "validate_data": self._validate_data_function
        }
        
        self.logger = logging.getLogger("WorkflowEngine")
        
        # Load workflows from files
        self.load_workflows()
    
    def register_workflow(self, workflow_def: WorkflowDefinition):
        """Register a new workflow definition."""
        self.workflows[workflow_def.workflow_id] = workflow_def
        self.logger.info(f"Registered workflow: {workflow_def.name}")
    
    def load_workflows(self):
        """Load workflow definitions from YAML files."""
        workflows_dir = Path("workflows")
        if not workflows_dir.exists():
            workflows_dir.mkdir()
            return
        
        for workflow_file in workflows_dir.glob("*.yaml"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = yaml.safe_load(f)
                
                workflow_def = self._parse_workflow_definition(workflow_data)
                self.register_workflow(workflow_def)
                
            except Exception as e:
                self.logger.error(f"Failed to load workflow {workflow_file}: {e}")
    
    def _parse_workflow_definition(self, data: Dict[str, Any]) -> WorkflowDefinition:
        """Parse workflow definition from YAML data."""
        steps = []
        for step_data in data.get("steps", []):
            # Parse condition if present
            condition = None
            if "condition" in step_data:
                cond_data = step_data["condition"]
                condition = WorkflowCondition(
                    variable=cond_data["variable"],
                    operator=ConditionOperator(cond_data["operator"]),
                    value=cond_data["value"],
                    source=cond_data.get("source", "output")
                )
            
            # Parse loop condition if present
            loop_condition = None
            if "loop_condition" in step_data:
                loop_data = step_data["loop_condition"]
                loop_condition = WorkflowCondition(
                    variable=loop_data["variable"],
                    operator=ConditionOperator(loop_data["operator"]),
                    value=loop_data["value"],
                    source=loop_data.get("source", "output")
                )
            
            step = WorkflowStep(
                step_id=step_data["step_id"],
                step_type=StepType(step_data["step_type"]),
                name=step_data["name"],
                description=step_data["description"],
                automation_system=step_data.get("automation_system"),
                task_type=step_data.get("task_type"),
                input_mapping=step_data.get("input_mapping", {}),
                output_mapping=step_data.get("output_mapping", {}),
                condition=condition,
                next_step_success=step_data.get("next_step_success"),
                next_step_failure=step_data.get("next_step_failure"),
                parallel_steps=step_data.get("parallel_steps", []),
                loop_condition=loop_condition,
                max_iterations=step_data.get("max_iterations", 10),
                timeout_seconds=step_data.get("timeout_seconds", 300),
                retry_count=step_data.get("retry_count", 3),
                retry_delay_seconds=step_data.get("retry_delay_seconds", 5),
                human_prompt=step_data.get("human_prompt"),
                human_options=step_data.get("human_options", [])
            )
            steps.append(step)
        
        return WorkflowDefinition(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            created_by=data["created_by"],
            created_at=datetime.fromisoformat(data["created_at"]),
            steps=steps,
            start_step=data["start_step"],
            input_schema=data.get("input_schema", {}),
            output_schema=data.get("output_schema", {}),
            tags=data.get("tags", []),
            category=data.get("category", "general"),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 30)
        )
    
    async def start_workflow(self, workflow_id: str, input_data: Dict[str, Any],
                           context: Dict[str, Any] = None) -> str:
        """Start a new workflow execution."""
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        workflow_def = self.workflows[workflow_id]
        execution_id = str(uuid.uuid4())
        
        # Store relevant context in knowledge base
        knowledge_base.store_context_snapshot(
            system_id="workflow_engine",
            user_context=context or {},
            task_context={"workflow_id": workflow_id, "execution_id": execution_id},
            environmental_context={},
            performance_metrics={}
        )
        
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.CREATED,
            current_step=workflow_def.start_step,
            input_data=input_data,
            output_data={},
            context=context or {},
            step_outputs={},
            started_at=datetime.now()
        )
        
        self.executions[execution_id] = execution
        
        # Queue for execution
        await self.execution_queue.put(execution_id)
        
        self.logger.info(f"Started workflow execution: {execution_id}")
        return execution_id
    
    async def process_executions(self):
        """Main loop for processing workflow executions."""
        while True:
            try:
                execution_id = await asyncio.wait_for(self.execution_queue.get(), timeout=1.0)
                await self._execute_workflow(execution_id)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing execution: {e}")
    
    async def _execute_workflow(self, execution_id: str):
        """Execute a workflow."""
        execution = self.executions[execution_id]
        workflow_def = self.workflows[execution.workflow_id]
        
        execution.status = WorkflowStatus.RUNNING
        
        try:
            current_step_id = execution.current_step
            
            while current_step_id:
                step = self._find_step(workflow_def, current_step_id)
                if not step:
                    raise ValueError(f"Step not found: {current_step_id}")
                
                self.logger.info(f"Executing step: {step.name}")
                
                # Execute step
                step_result = await self._execute_step(execution, workflow_def, step)
                
                # Store step output
                execution.step_outputs[step.step_id] = step_result
                execution.executed_steps.append(step.step_id)
                
                # Determine next step
                next_step_id = self._determine_next_step(step, step_result)
                current_step_id = next_step_id
                execution.current_step = current_step_id
            
            # Workflow completed
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()
            
            # Generate output based on output schema
            execution.output_data = self._generate_workflow_output(
                workflow_def, execution
            )
            
            self.logger.info(f"Workflow completed: {execution_id}")
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            
            self.logger.error(f"Workflow failed: {execution_id} - {e}")
    
    async def _execute_step(self, execution: WorkflowExecution,
                           workflow_def: WorkflowDefinition,
                           step: WorkflowStep) -> Dict[str, Any]:
        """Execute an individual workflow step."""
        
        if step.step_type == StepType.TASK:
            return await self._execute_task_step(execution, step)
        elif step.step_type == StepType.CONDITION:
            return await self._execute_condition_step(execution, step)
        elif step.step_type == StepType.LOOP:
            return await self._execute_loop_step(execution, workflow_def, step)
        elif step.step_type == StepType.PARALLEL:
            return await self._execute_parallel_step(execution, workflow_def, step)
        elif step.step_type == StepType.WAIT:
            return await self._execute_wait_step(execution, step)
        elif step.step_type == StepType.HUMAN_INPUT:
            return await self._execute_human_input_step(execution, step)
        elif step.step_type == StepType.DECISION:
            return await self._execute_decision_step(execution, step)
        else:
            raise ValueError(f"Unknown step type: {step.step_type}")
    
    async def _execute_task_step(self, execution: WorkflowExecution,
                                step: WorkflowStep) -> Dict[str, Any]:
        """Execute a task step."""
        
        # Prepare input data for the task
        task_input = self._prepare_task_input(execution, step)
        
        # Create automation task
        task = AutomationTask(
            task_id=str(uuid.uuid4()),
            automation_id=step.automation_system,
            task_type=step.task_type,
            description=f"Workflow step: {step.name}",
            priority=Priority.MEDIUM,
            status=AutomationStatus.IDLE,
            input_data=task_input
        )
        
        # Submit task to orchestrator
        task_id = await orchestrator.submit_task(task)
        
        # Wait for completion (with timeout)
        start_time = datetime.now()
        while True:
            await asyncio.sleep(1)
            
            # Check timeout
            if (datetime.now() - start_time).total_seconds() > step.timeout_seconds:
                raise TimeoutError(f"Step timeout: {step.name}")
            
            # Check task status
            if task_id in orchestrator.active_tasks:
                current_task = orchestrator.active_tasks[task_id]
                
                if current_task.status == AutomationStatus.COMPLETED:
                    return self._map_task_output(current_task.output_data, step)
                elif current_task.status == AutomationStatus.FAILED:
                    raise RuntimeError(f"Task failed: {current_task.error_message}")
                elif current_task.status == AutomationStatus.WAITING_HUMAN:
                    # Handle human intervention in workflow context
                    return await self._handle_task_human_intervention(current_task)
            else:
                # Task might be completed and moved
                for completed_task in orchestrator.completed_tasks:
                    if completed_task.task_id == task_id:
                        return self._map_task_output(completed_task.output_data, step)
    
    async def _execute_condition_step(self, execution: WorkflowExecution,
                                     step: WorkflowStep) -> Dict[str, Any]:
        """Execute a condition step."""
        
        if not step.condition:
            raise ValueError(f"Condition step missing condition: {step.step_id}")
        
        result = self._evaluate_condition(execution, step.condition)
        
        return {
            "condition_result": result,
            "condition_variable": step.condition.variable,
            "condition_value": step.condition.value
        }
    
    async def _execute_loop_step(self, execution: WorkflowExecution,
                                workflow_def: WorkflowDefinition,
                                step: WorkflowStep) -> Dict[str, Any]:
        """Execute a loop step."""
        
        iterations = 0
        loop_results = []
        
        while iterations < step.max_iterations:
            # Check loop condition
            if step.loop_condition:
                should_continue = self._evaluate_condition(execution, step.loop_condition)
                if not should_continue:
                    break
            
            # Execute loop body (parallel steps)
            iteration_results = {}
            for substep_id in step.parallel_steps:
                substep = self._find_step(workflow_def, substep_id)
                if substep:
                    result = await self._execute_step(execution, workflow_def, substep)
                    iteration_results[substep_id] = result
            
            loop_results.append(iteration_results)
            iterations += 1
        
        return {
            "iterations": iterations,
            "loop_results": loop_results
        }
    
    async def _execute_parallel_step(self, execution: WorkflowExecution,
                                    workflow_def: WorkflowDefinition,
                                    step: WorkflowStep) -> Dict[str, Any]:
        """Execute parallel steps."""
        
        # Create tasks for all parallel steps
        tasks = []
        for substep_id in step.parallel_steps:
            substep = self._find_step(workflow_def, substep_id)
            if substep:
                task = asyncio.create_task(
                    self._execute_step(execution, workflow_def, substep)
                )
                tasks.append((substep_id, task))
        
        # Wait for all tasks to complete
        results = {}
        for substep_id, task in tasks:
            try:
                result = await task
                results[substep_id] = result
            except Exception as e:
                results[substep_id] = {"error": str(e)}
        
        return {"parallel_results": results}
    
    async def _execute_wait_step(self, execution: WorkflowExecution,
                                step: WorkflowStep) -> Dict[str, Any]:
        """Execute a wait step."""
        
        wait_seconds = step.input_mapping.get("duration", 5)
        await asyncio.sleep(wait_seconds)
        
        return {"waited_seconds": wait_seconds}
    
    async def _execute_human_input_step(self, execution: WorkflowExecution,
                                       step: WorkflowStep) -> Dict[str, Any]:
        """Execute a human input step."""
        
        from automation_ecosystem import HumanInterventionRequest, InterventionType
        
        # Create human intervention request
        intervention = HumanInterventionRequest(
            request_id=str(uuid.uuid4()),
            automation_id="workflow_engine",
            intervention_type=InterventionType.DECISION_REQUIRED,
            priority=Priority.MEDIUM,
            title=f"Workflow Input Required: {step.name}",
            description=step.human_prompt or f"Input required for step: {step.description}",
            context={
                "workflow_id": execution.workflow_id,
                "execution_id": execution.execution_id,
                "step_id": step.step_id
            },
            options=step.human_options,
            deadline=datetime.now() + timedelta(hours=24),
            callback_function="resolve_workflow_human_input",
            created_at=datetime.now()
        )
        
        # Register intervention
        orchestrator.pending_interventions[intervention.request_id] = intervention
        
        # Wait for resolution (simplified - in real implementation, use proper async)
        while intervention.request_id in orchestrator.pending_interventions:
            await asyncio.sleep(1)
        
        # Get resolution
        if intervention.resolution:
            return intervention.resolution
        else:
            raise RuntimeError("Human input not provided")
    
    async def _execute_decision_step(self, execution: WorkflowExecution,
                                    step: WorkflowStep) -> Dict[str, Any]:
        """Execute a decision step using knowledge base."""
        
        # Get relevant context from knowledge base
        context = knowledge_base.get_relevant_context(
            system_id="workflow_engine",
            task_type="decision",
            keywords=[execution.workflow_id, step.step_id]
        )
        
        # Use context to make decision (simplified)
        decision = "continue"  # Default decision
        
        # Store decision context for future learning
        knowledge_base.store_knowledge(
            category="decision",
            source_system="workflow_engine",
            title=f"Decision for {step.name}",
            content={
                "decision": decision,
                "context": context,
                "step_info": asdict(step)
            },
            tags=["workflow", "decision", execution.workflow_id],
            confidence_score=0.8
        )
        
        return {"decision": decision, "context_used": bool(context)}
    
    def _prepare_task_input(self, execution: WorkflowExecution,
                           step: WorkflowStep) -> Dict[str, Any]:
        """Prepare input data for a task based on input mapping."""
        
        task_input = {}
        
        for task_param, source_path in step.input_mapping.items():
            value = self._resolve_value_path(execution, source_path)
            task_input[task_param] = value
        
        return task_input
    
    def _map_task_output(self, task_output: Dict[str, Any],
                        step: WorkflowStep) -> Dict[str, Any]:
        """Map task output based on output mapping."""
        
        if not step.output_mapping:
            return task_output
        
        mapped_output = {}
        for output_key, task_output_path in step.output_mapping.items():
            if task_output_path in task_output:
                mapped_output[output_key] = task_output[task_output_path]
        
        return mapped_output
    
    def _resolve_value_path(self, execution: WorkflowExecution, path: str) -> Any:
        """Resolve a value path (e.g., 'input.dataset_path', 'step1.output.result')."""
        
        parts = path.split('.')
        
        if parts[0] == "input":
            current = execution.input_data
        elif parts[0] == "context":
            current = execution.context
        elif parts[0].startswith("step"):
            step_id = parts[0]
            if step_id in execution.step_outputs:
                current = execution.step_outputs[step_id]
            else:
                return None
        else:
            return path  # Return as literal value
        
        # Navigate through the path
        for part in parts[1:]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _evaluate_condition(self, execution: WorkflowExecution,
                           condition: WorkflowCondition) -> bool:
        """Evaluate a workflow condition."""
        
        # Get the variable value
        if condition.source == "output":
            var_value = self._resolve_value_path(execution, condition.variable)
        elif condition.source == "context":
            var_value = execution.context.get(condition.variable)
        else:
            var_value = condition.variable
        
        # Evaluate based on operator
        if condition.operator == ConditionOperator.EQUALS:
            return var_value == condition.value
        elif condition.operator == ConditionOperator.NOT_EQUALS:
            return var_value != condition.value
        elif condition.operator == ConditionOperator.GREATER_THAN:
            return var_value > condition.value
        elif condition.operator == ConditionOperator.LESS_THAN:
            return var_value < condition.value
        elif condition.operator == ConditionOperator.CONTAINS:
            return condition.value in str(var_value)
        elif condition.operator == ConditionOperator.NOT_CONTAINS:
            return condition.value not in str(var_value)
        elif condition.operator == ConditionOperator.EXISTS:
            return var_value is not None
        elif condition.operator == ConditionOperator.NOT_EXISTS:
            return var_value is None
        
        return False
    
    def _determine_next_step(self, step: WorkflowStep,
                            step_result: Dict[str, Any]) -> Optional[str]:
        """Determine the next step based on step result."""
        
        # For condition steps, check the result
        if step.step_type == StepType.CONDITION:
            if step_result.get("condition_result", False):
                return step.next_step_success
            else:
                return step.next_step_failure
        
        # For other steps, check if there was an error
        if "error" in step_result:
            return step.next_step_failure
        else:
            return step.next_step_success
    
    def _find_step(self, workflow_def: WorkflowDefinition,
                   step_id: str) -> Optional[WorkflowStep]:
        """Find a step by ID in the workflow definition."""
        
        for step in workflow_def.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _generate_workflow_output(self, workflow_def: WorkflowDefinition,
                                 execution: WorkflowExecution) -> Dict[str, Any]:
        """Generate final workflow output based on output schema."""
        
        output = {}
        
        for output_key, source_path in workflow_def.output_schema.items():
            value = self._resolve_value_path(execution, source_path)
            output[output_key] = value
        
        return output
    
    async def _handle_task_human_intervention(self, task) -> Dict[str, Any]:
        """Handle human intervention for a task within workflow."""
        
        # Wait for intervention to be resolved
        while task.status == AutomationStatus.WAITING_HUMAN:
            await asyncio.sleep(1)
        
        if task.status == AutomationStatus.COMPLETED:
            return task.output_data or {}
        else:
            raise RuntimeError(f"Task failed after human intervention: {task.error_message}")
    
    # Built-in workflow functions
    async def _wait_function(self, duration: int) -> Dict[str, Any]:
        """Built-in wait function."""
        await asyncio.sleep(duration)
        return {"waited": duration}
    
    async def _log_function(self, message: str, level: str = "info") -> Dict[str, Any]:
        """Built-in log function."""
        getattr(self.logger, level.lower())(message)
        return {"logged": message}
    
    async def _set_variable_function(self, variable: str, value: Any) -> Dict[str, Any]:
        """Built-in set variable function."""
        return {variable: value}
    
    async def _send_notification_function(self, message: str, channel: str = "default") -> Dict[str, Any]:
        """Built-in notification function."""
        # In real implementation, send actual notification
        self.logger.info(f"Notification [{channel}]: {message}")
        return {"notification_sent": True, "message": message}
    
    async def _validate_data_function(self, data: Any, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Built-in data validation function."""
        # Simple validation (in real implementation, use jsonschema)
        is_valid = isinstance(data, dict)  # Simplified
        return {"is_valid": is_valid, "data": data}
    
    def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow execution."""
        
        if execution_id not in self.executions:
            return None
        
        execution = self.executions[execution_id]
        workflow_def = self.workflows[execution.workflow_id]
        
        return {
            "execution_id": execution_id,
            "workflow_name": workflow_def.name,
            "status": execution.status.value,
            "current_step": execution.current_step,
            "progress": len(execution.executed_steps) / len(workflow_def.steps),
            "started_at": execution.started_at.isoformat(),
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
            "error_message": execution.error_message
        }
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows."""
        
        return [
            {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "description": wf.description,
                "category": wf.category,
                "estimated_duration": wf.estimated_duration_minutes,
                "steps_count": len(wf.steps)
            }
            for wf in self.workflows.values()
        ]

# Global workflow engine instance
workflow_engine = WorkflowEngine()
