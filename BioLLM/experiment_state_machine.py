#!/usr/bin/env python3
"""
Experiment State Machine - Manages the state transitions for execute experiment triggers
"""

from enum import Enum
from typing import Optional, Dict, Any
import streamlit as st


class ExperimentState(Enum):
    """Experiment state enumeration"""
    INITIAL = 1
    ANALYSIS_CONFIRMED = 2


class ExperimentTrigger(Enum):
    """Experiment trigger types"""
    ANALYSE_AGENT_YES = "analyse_agent_yes"
    EXPLAIN_AGENT_YES = "explain_agent_yes"
    RESET = "reset"


class ExperimentStateMachine:
    """
    State machine for managing execute experiment triggers
    
    States:
    - INITIAL (1): Initial state, waiting for analyse agent confirmation
    - ANALYSIS_CONFIRMED (2): Analyse agent confirmed, waiting for explain agent confirmation
    
    Transitions:
    - INITIAL + ANALYSE_AGENT_YES -> ANALYSIS_CONFIRMED
    - ANALYSIS_CONFIRMED + EXPLAIN_AGENT_YES -> INITIAL (triggers execute experiment)
    - Any state + RESET -> INITIAL
    """
    
    def __init__(self):
        """Initialize the state machine"""
        self.current_state = ExperimentState.INITIAL
        self.analyse_model_name: Optional[str] = None
        self.analyse_task_type: Optional[int] = None
        self.explain_model_name: Optional[str] = None
        self.explain_task_type: Optional[int] = None
        
    def get_current_state(self) -> ExperimentState:
        """Get current state"""
        return self.current_state
    
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information"""
        return {
            'state': self.current_state.value,
            'state_name': self.current_state.name,
            'analyse_model_name': self.analyse_model_name,
            'analyse_task_type': self.analyse_task_type,
            'explain_model_name': self.explain_model_name,
            'explain_task_type': self.explain_task_type
        }
    
    def transition(self, trigger: ExperimentTrigger, **kwargs) -> Dict[str, Any]:
        """
        Perform state transition based on trigger
        
        Args:
            trigger: The trigger that caused the transition
            **kwargs: Additional parameters (model_name, task_type, etc.)
            
        Returns:
            Dict containing transition result and whether experiment should be executed
        """
        result = {
            'transition_successful': False,
            'new_state': self.current_state,
            'should_execute_experiment': False,
            'experiment_params': None,
            'message': ''
        }
        
        if trigger == ExperimentTrigger.ANALYSE_AGENT_YES:
            if self.current_state == ExperimentState.INITIAL:
                # Transition from INITIAL to ANALYSIS_CONFIRMED
                self.current_state = ExperimentState.ANALYSIS_CONFIRMED
                self.analyse_model_name = kwargs.get('model_name')
                self.analyse_task_type = kwargs.get('task_type')
                
                result['transition_successful'] = True
                result['new_state'] = self.current_state
                result['message'] = f"✅ Analysis confirmed for {self.analyse_model_name}. Waiting for explanation confirmation..."
                
            else:
                result['message'] = f"❌ Invalid transition: Cannot confirm analysis in state {self.current_state.name}"
                
        elif trigger == ExperimentTrigger.EXPLAIN_AGENT_YES:
            if self.current_state == ExperimentState.ANALYSIS_CONFIRMED:
                # Transition from ANALYSIS_CONFIRMED to INITIAL and trigger experiment
                self.explain_model_name = kwargs.get('model_name')
                self.explain_task_type = kwargs.get('task_type')
                
                # Verify that explain parameters match analyse parameters
                if (self.explain_model_name == self.analyse_model_name and 
                    self.explain_task_type == self.analyse_task_type):
                    
                    # Prepare experiment parameters
                    experiment_params = {
                        'model_name': self.explain_model_name,
                        'task_type': self.explain_task_type
                    }
                    
                    # Reset to initial state
                    self._reset()
                    
                    result['transition_successful'] = True
                    result['new_state'] = self.current_state
                    result['should_execute_experiment'] = True
                    result['experiment_params'] = experiment_params
                    result['message'] = f"🎉 Experiment execution triggered for {experiment_params['model_name']}!"
                    
                else:
                    result['message'] = f"❌ Parameter mismatch: Analyse ({self.analyse_model_name}, {self.analyse_task_type}) vs Explain ({self.explain_model_name}, {self.explain_task_type})"
                    
            else:
                result['message'] = f"❌ Invalid transition: Cannot confirm explanation in state {self.current_state.name}"
                
        elif trigger == ExperimentTrigger.RESET:
            # Reset to initial state
            self._reset()
            result['transition_successful'] = True
            result['new_state'] = self.current_state
            result['message'] = "🔄 State machine reset to initial state"
            
        else:
            result['message'] = f"❌ Unknown trigger: {trigger}"
            
        return result
    
    def _reset(self):
        """Reset state machine to initial state"""
        self.current_state = ExperimentState.INITIAL
        self.analyse_model_name = None
        self.analyse_task_type = None
        self.explain_model_name = None
        self.explain_task_type = None
    
    def can_trigger_experiment(self) -> bool:
        """Check if experiment can be triggered in current state"""
        return (self.current_state == ExperimentState.ANALYSIS_CONFIRMED and 
                self.analyse_model_name is not None and 
                self.analyse_task_type is not None)
    
    def get_expected_next_trigger(self) -> Optional[ExperimentTrigger]:
        """Get the expected next trigger based on current state"""
        if self.current_state == ExperimentState.INITIAL:
            return ExperimentTrigger.ANALYSE_AGENT_YES
        elif self.current_state == ExperimentState.ANALYSIS_CONFIRMED:
            return ExperimentTrigger.EXPLAIN_AGENT_YES
        else:
            return None


# Global state machine instance
_state_machine = None

def get_state_machine() -> ExperimentStateMachine:
    """Get the global state machine instance"""
    global _state_machine
    if _state_machine is None:
        _state_machine = ExperimentStateMachine()
    return _state_machine

def reset_state_machine():
    """Reset the global state machine"""
    global _state_machine
    if _state_machine is not None:
        _state_machine._reset()

def handle_analyse_agent_response(user_input: str, model_name: str, task_type: int) -> Dict[str, Any]:
    """
    Handle response to analyse agent prompt
    
    Args:
        user_input: User's response
        model_name: Model name from analyse agent
        task_type: Task type from analyse agent
        
    Returns:
        Dict containing transition result
    """
    from agent.judge_agent import judge_user_response
    
    state_machine = get_state_machine()
    
    # Check if user response is positive
    if judge_user_response(user_input):
        # Trigger state transition
        return state_machine.transition(
            ExperimentTrigger.ANALYSE_AGENT_YES,
            model_name=model_name,
            task_type=task_type
        )
    else:
        # User declined, reset state machine
        return state_machine.transition(ExperimentTrigger.RESET)

def handle_explain_agent_response(user_input: str, model_name: str, task_type: int) -> Dict[str, Any]:
    """
    Handle response to explain agent prompt
    
    Args:
        user_input: User's response
        model_name: Model name from explain agent
        task_type: Task type from explain agent
        
    Returns:
        Dict containing transition result
    """
    from agent.judge_agent import judge_user_response
    
    state_machine = get_state_machine()
    
    # Check if user response is positive
    if judge_user_response(user_input):
        # Trigger state transition
        return state_machine.transition(
            ExperimentTrigger.EXPLAIN_AGENT_YES,
            model_name=model_name,
            task_type=task_type
        )
    else:
        # User declined, reset state machine
        return state_machine.transition(ExperimentTrigger.RESET)

def get_current_state_info() -> Dict[str, Any]:
    """Get current state information"""
    state_machine = get_state_machine()
    return state_machine.get_state_info()
