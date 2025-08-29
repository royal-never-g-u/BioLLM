#!/usr/bin/env python3
"""
BioTask Module - For managing biological model analysis tasks
"""

import json
import os
from typing import Dict, Union, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

# Import analysis types
try:
    from analysis_types import ANALYSIS_TYPES, get_analysis_type_description, is_valid_analysis_id
except ImportError:
    # Fallback if analysis_types module is not available
    ANALYSIS_TYPES = {
        1: "Flux Balance Analysis (FBA)",
        2: "Gene Knockout Analysis", 
        3: "Phenotype Prediction",
        4: "Pathway Analysis",
        5: "Evolutionary Analysis",
        6: "Constraint-Based Analysis"
    }
    
    def get_analysis_type_description(analysis_id: int) -> str:
        return ANALYSIS_TYPES.get(analysis_id)
    
    def is_valid_analysis_id(analysis_id: int) -> bool:
        return analysis_id in ANALYSIS_TYPES


@dataclass
class BioTask:
    """
    Biological model analysis task class
    
    Attributes:
        model_name (str): Model name
        model_local (str): Model local path
        task_type (Union[int, str]): Task type, can be integer (1-6) or string description
    """
    model_name: str = ""
    model_local: str = ""
    task_type: Union[int, str] = ""
    
    def get_task_type_description(self) -> str:
        """
        Get the description of the task type
        
        Returns:
            str: Task type description
        """
        if isinstance(self.task_type, int):
            return get_analysis_type_description(self.task_type) or f"Unknown Analysis Type (ID: {self.task_type})"
        elif isinstance(self.task_type, str):
            # If it's already a string description, return it
            return self.task_type
        else:
            return str(self.task_type)
    
    def is_valid_task_type(self) -> bool:
        """
        Check if the task type is valid
        
        Returns:
            bool: True if task type is valid, False otherwise
        """
        if isinstance(self.task_type, int):
            return is_valid_analysis_id(self.task_type)
        elif isinstance(self.task_type, str):
            # Check if the string matches any of the analysis type descriptions
            return self.task_type in ANALYSIS_TYPES.values()
        else:
            return False

    def to_dict(self) -> Dict:
        """Convert BioTask object to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'BioTask':
        """Create BioTask object from dictionary"""
        return cls(**data)


class BioTaskManager:
    """BioTask manager, responsible for JSON file read/write operations"""
    
    def __init__(self, temp_dir: str = "Temp"):
        """
        Initialize BioTask manager
        
        Args:
            temp_dir (str): Temporary folder path, defaults to "Temp"
        """
        self.temp_dir = Path(temp_dir)
        self.json_file_path = self.temp_dir / "bio_task.json"
        
        # Ensure temporary folder exists
        self.temp_dir.mkdir(exist_ok=True)
    
    def initialize_task_file(self) -> None:
        """
        Initialize task file, always clear content and create empty BioTask object
        File will be reset to empty state on every program run
        """
        empty_task = BioTask()
        self.save_task(empty_task)
        print(f"BioTask file initialized (cleared): {self.json_file_path}")
    
    def save_task(self, task: BioTask) -> None:
        """
        Save BioTask object to JSON file
        
        Args:
            task (BioTask): BioTask object to save
        """
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(task.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving BioTask: {e}")
            raise
    
    def load_task(self) -> Optional[BioTask]:
        """
        Load BioTask object from JSON file
        
        Returns:
            Optional[BioTask]: Loaded BioTask object, returns None if file doesn't exist or read fails
        """
        try:
            if not self.json_file_path.exists():
                print(f"BioTask file does not exist: {self.json_file_path}")
                return None
            
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return BioTask.from_dict(data)
        except Exception as e:
            print(f"Error loading BioTask: {e}")
            return None
    
    def update_task(self, **kwargs) -> bool:
        """
        Update BioTask object attributes
        
        Args:
            **kwargs: Attributes to update, such as model_name="new_name", task_type=1
            
        Returns:
            bool: Whether update was successful
        """
        try:
            task = self.load_task()
            if task is None:
                task = BioTask()
            
            # Update attributes
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
                else:
                    print(f"Warning: BioTask does not have attribute '{key}'")
            
            self.save_task(task)
            return True
        except Exception as e:
            print(f"Error updating BioTask: {e}")
            return False
    
    def get_task_info(self) -> Optional[Dict]:
        """
        Get current BioTask information
        
        Returns:
            Optional[Dict]: Dictionary representation of BioTask, returns None if loading fails
        """
        task = self.load_task()
        return task.to_dict() if task else None
    
    def clear_task(self) -> None:
        """Clear BioTask file content, reset to empty object"""
        self.initialize_task_file()
    
    def get_available_analysis_types(self) -> Dict[int, str]:
        """
        Get all available analysis types
        
        Returns:
            Dict[int, str]: Dictionary of available analysis types
        """
        return ANALYSIS_TYPES.copy()
    
    def validate_task_type(self, task_type: Union[int, str]) -> bool:
        """
        Validate if the given task type is valid
        
        Args:
            task_type (Union[int, str]): Task type to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if isinstance(task_type, int):
            return is_valid_analysis_id(task_type)
        elif isinstance(task_type, str):
            return task_type in ANALYSIS_TYPES.values()
        else:
            return False
    
    def get_task_type_description(self, task_type: Union[int, str]) -> str:
        """
        Get description for the given task type
        
        Args:
            task_type (Union[int, str]): Task type
            
        Returns:
            str: Task type description
        """
        if isinstance(task_type, int):
            return get_analysis_type_description(task_type) or f"Unknown Analysis Type (ID: {task_type})"
        elif isinstance(task_type, str):
            return task_type
        else:
            return str(task_type)


# Global BioTask manager instance
bio_task_manager = BioTaskManager()


def initialize_bio_task() -> None:
    """Called when project starts, initialize BioTask file"""
    bio_task_manager.initialize_task_file()


def get_current_task() -> Optional[BioTask]:
    """Get current BioTask object"""
    return bio_task_manager.load_task()


def update_current_task(**kwargs) -> bool:
    """
    Update current BioTask object attributes
    
    This function should only be called by:
    1. task_pick_agent (for task_type updates)
    2. analyse command user response (for model_name updates)
    3. program startup (for initialization)
    
    All other calls should be avoided to prevent unauthorized modifications.
    """
    return bio_task_manager.update_task(**kwargs)


def save_current_task(task: BioTask) -> None:
    """Save BioTask object to file"""
    bio_task_manager.save_task(task)


def get_available_analysis_types() -> Dict[int, str]:
    """Get all available analysis types"""
    return bio_task_manager.get_available_analysis_types()


def validate_task_type(task_type: Union[int, str]) -> bool:
    """Validate if the given task type is valid"""
    return bio_task_manager.validate_task_type(task_type)


def get_task_type_description(task_type: Union[int, str]) -> str:
    """Get description for the given task type"""
    return bio_task_manager.get_task_type_description(task_type)


if __name__ == "__main__":
    # Test code
    print("Testing BioTask functionality with analysis types...")
    
    # Initialize task file
    initialize_bio_task()
    
    # Test 1: Create and save a task with integer task type
    print("\n=== Test 1: Integer task type ===")
    task = BioTask(
        model_name="E. coli core model",
        model_local="/path/to/model",
        task_type=2  # Gene Knockout Analysis
    )
    save_current_task(task)
    
    # Load task and test new methods
    loaded_task = get_current_task()
    print(f"Loaded task: {loaded_task}")
    print(f"Task type description: {loaded_task.get_task_type_description()}")
    print(f"Is valid task type: {loaded_task.is_valid_task_type()}")
    
    # Test 2: Update task with string task type
    print("\n=== Test 2: String task type ===")
    update_current_task(
        model_name="Updated model name", 
        task_type="Flux Balance Analysis (FBA)"
    )
    
    # Get updated task information
    task_info = bio_task_manager.get_task_info()
    print(f"Updated task information: {task_info}")
    
    # Test 3: Test analysis type functions
    print("\n=== Test 3: Analysis type functions ===")
    available_types = get_available_analysis_types()
    print("Available analysis types:")
    for key, value in available_types.items():
        print(f"  {key}: {value}")
    
    # Test validation
    test_types = [1, 2, 7, "Flux Balance Analysis (FBA)", "Invalid Type"]
    print("\nTask type validation:")
    for test_type in test_types:
        is_valid = validate_task_type(test_type)
        description = get_task_type_description(test_type)
        print(f"  {test_type}: Valid={is_valid}, Description={description}")
    
    # Test 4: Test BioTask methods with different types
    print("\n=== Test 4: BioTask methods ===")
    test_task = BioTask(
        model_name="Test Model",
        model_local="/test/path",
        task_type=3  # Phenotype Prediction
    )
    print(f"Task: {test_task}")
    print(f"Task type description: {test_task.get_task_type_description()}")
    print(f"Is valid: {test_task.is_valid_task_type()}")
    
    # Test with invalid task type
    invalid_task = BioTask(
        model_name="Invalid Model",
        model_local="/invalid/path",
        task_type=99  # Invalid ID
    )
    print(f"Invalid task: {invalid_task}")
    print(f"Task type description: {invalid_task.get_task_type_description()}")
    print(f"Is valid: {invalid_task.is_valid_task_type()}")
