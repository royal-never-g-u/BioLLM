#!/usr/bin/env python3
"""
Task Pick Agent - Analyzes user input and matches it to analysis types
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List, Tuple

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bio_task import update_current_task, get_current_task
from analysis_types import ANALYSIS_TYPES, TASK_PROMPT

class TaskPickAgent:
    """
    Agent that analyzes user input and matches it to analysis types
    """
    
    def __init__(self):
        """Initialize the TaskPickAgent"""
        self.analysis_types = ANALYSIS_TYPES
        self.task_prompt = TASK_PROMPT
        
    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Analyze user input and determine if it matches any analysis type
        
        Args:
            user_input (str): User's input text
            
        Returns:
            Dict containing analysis results and matched task type
        """
        try:
            print(f"🔍 TaskPickAgent: Analyzing user input: '{user_input}'")
            
            # Create LLM prompt for analysis
            llm_prompt = self._create_analysis_prompt(user_input)
            
            # Simulate LLM analysis (in real implementation, this would call an actual LLM)
            analysis_result = self._simulate_llm_analysis(llm_prompt, user_input)
            
            # Process the analysis result
            matched_task_type = self._process_analysis_result(analysis_result, user_input)
            
            # Update bio_task only if a valid match is found
            if matched_task_type is not None:
                self._update_bio_task(matched_task_type)
                
                # Check if we should trigger if_next_step
                next_step_result = self._check_and_trigger_next_step()
                
                return {
                    'success': True,
                    'user_input': user_input,
                    'matched_task_type': matched_task_type,
                    'analysis_result': analysis_result,
                    'bio_task_updated': True,
                    'next_step_triggered': next_step_result is not None,
                    'next_step_result': next_step_result
                }
            else:
                # Don't update bio_task if no match found, preserve existing task_type
                print(f"ℹ️ TaskPickAgent: 未匹配到分析类型，保持现有task_type不变")
                
                return {
                    'success': True,
                    'user_input': user_input,
                    'matched_task_type': matched_task_type,
                    'analysis_result': analysis_result,
                    'bio_task_updated': False,
                    'next_step_triggered': False,
                    'next_step_result': None
                }
            
        except Exception as e:
            print(f"❌ Error in TaskPickAgent: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_input': user_input,
                'matched_task_type': None,
                'bio_task_updated': False
            }
    
    def _create_analysis_prompt(self, user_input: str) -> str:
        """
        Create LLM prompt for analyzing user input
        
        Args:
            user_input (str): User's input text
            
        Returns:
            str: Formatted prompt for LLM analysis
        """
        prompt = f"""
请分析以下用户输入，判断它是否匹配以下分析类型中的某一个。

可用的分析类型：
{self._format_analysis_types()}

任务说明：
{self.task_prompt}

用户输入："{user_input}"

请按照以下格式回答：

1. 是否匹配：是/否
2. 匹配的分析类型ID（如果匹配）：1-6的数字
3. 匹配的分析类型名称（如果匹配）：完整的分析类型名称
4. 匹配理由：简要说明为什么匹配或不匹配
5. 置信度：高/中/低

示例回答：
1. 是否匹配：是
2. 匹配的分析类型ID：2
3. 匹配的分析类型名称：Gene Knockout Analysis
4. 匹配理由：用户提到了"基因敲除"和"删除基因"，这与基因敲除分析直接相关
5. 置信度：高

请分析上述用户输入：
"""
        return prompt
    
    def _format_analysis_types(self) -> str:
        """
        Format analysis types for display
        
        Returns:
            str: Formatted analysis types string
        """
        formatted = ""
        for key, value in self.analysis_types.items():
            formatted += f"{key}. {value}\n"
        return formatted
    
    def _simulate_llm_analysis(self, prompt: str, user_input: str) -> Dict[str, Any]:
        """
        Simulate LLM analysis (in real implementation, this would call an actual LLM)
        
        Args:
            prompt (str): LLM prompt
            user_input (str): User input for context
            
        Returns:
            Dict containing simulated LLM response
        """
        # This is a simulation - in real implementation, you would call an actual LLM
        # For now, we'll use a simple keyword matching approach
        
        user_input_lower = user_input.lower()
        
        # Define keywords for each analysis type
        keywords = {
            1: ['flux balance', 'fba', '通量平衡', '代谢通量', 'flux', 'balance', '1'],
            2: ['gene knockout', 'gene deletion', '基因敲除', '基因删除', 'knockout', 'deletion', '2'],
            3: ['phenotype', '表型', 'phenotype prediction', '表型预测', '3'],
            4: ['pathway', '途径', 'pathway analysis', '途径分析', '4'],
            5: ['evolutionary', '进化', 'evolution', 'evolutionary analysis', '进化分析', '5'],
            6: ['constraint', '约束', 'constraint-based', '约束基础', '6']
        }
        
        # Find matches
        matches = []
        for analysis_id, keyword_list in keywords.items():
            for keyword in keyword_list:
                if keyword in user_input_lower:
                    matches.append({
                        'analysis_id': analysis_id,
                        'analysis_name': self.analysis_types[analysis_id],
                        'matched_keyword': keyword,
                        'confidence': 'high' if len(keyword) > 3 else 'medium'
                    })
                    break  # Only match once per analysis type
        
        if matches:
            # Return the best match (first one found)
            best_match = matches[0]
            return {
                'is_match': True,
                'analysis_id': best_match['analysis_id'],
                'analysis_name': best_match['analysis_name'],
                'matched_keyword': best_match['matched_keyword'],
                'confidence': best_match['confidence'],
                'reason': f"用户输入包含关键词 '{best_match['matched_keyword']}'，匹配分析类型 '{best_match['analysis_name']}'"
            }
        else:
            return {
                'is_match': False,
                'analysis_id': None,
                'analysis_name': None,
                'matched_keyword': None,
                'confidence': 'low',
                'reason': "用户输入中没有找到与分析类型相关的关键词"
            }
    
    def _process_analysis_result(self, analysis_result: Dict[str, Any], user_input: str) -> Optional[int]:
        """
        Process LLM analysis result and extract matched task type
        
        Args:
            analysis_result (Dict): LLM analysis result
            user_input (str): Original user input
            
        Returns:
            Optional[int]: Matched task type ID or None
        """
        if analysis_result.get('is_match', False):
            analysis_id = analysis_result.get('analysis_id')
            analysis_name = analysis_result.get('analysis_name')
            confidence = analysis_result.get('confidence', 'low')
            
            print(f"✅ TaskPickAgent: 匹配到分析类型 {analysis_id} - {analysis_name}")
            print(f"   置信度: {confidence}")
            print(f"   匹配理由: {analysis_result.get('reason', 'N/A')}")
            
            return analysis_id
        else:
            print(f"❌ TaskPickAgent: 未匹配到任何分析类型")
            print(f"   原因: {analysis_result.get('reason', 'N/A')}")
            return None
    
    def _update_bio_task(self, task_type: int) -> bool:
        """
        Update bio_task with the matched task type
        
        Args:
            task_type (int): Task type ID to set
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Get current task to preserve other fields
            current_task = get_current_task()
            
            # Update task type
            success = update_current_task(task_type=task_type)
            
            if success:
                print(f"✅ TaskPickAgent: 成功更新bio_task，设置task_type为 {task_type}")
                print(f"   分析类型: {self.analysis_types.get(task_type, 'Unknown')}")
            else:
                print(f"❌ TaskPickAgent: 更新bio_task失败")
            
            return success
            
        except Exception as e:
            print(f"❌ TaskPickAgent: 更新bio_task时出错: {e}")
            return False
    
    def get_available_analysis_types(self) -> Dict[int, str]:
        """
        Get all available analysis types
        
        Returns:
            Dict[int, str]: Dictionary of available analysis types
        """
        return self.analysis_types.copy()
    
    def validate_task_type(self, task_type: int) -> bool:
        """
        Validate if a task type is valid
        
        Args:
            task_type (int): Task type to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return task_type in self.analysis_types
    
    def _check_and_trigger_next_step(self) -> Optional[Dict[str, Any]]:
        """
        Check if bio_task has both model_name and task_type, and trigger if_next_step if so
        
        Returns:
            Optional[Dict[str, Any]]: Next step result if triggered, None otherwise
        """
        try:
            # Get current bio_task
            current_task = get_current_task()
            
            # Check if both model_name and task_type exist
            has_model_name = bool(current_task.model_name and current_task.model_name.strip())
            has_task_type = current_task.task_type is not None and current_task.task_type != ""
            
            if has_model_name and has_task_type:
                print(f"🎯 TaskPickAgent: 检测到完整配置 (model_name: {current_task.model_name}, task_type: {current_task.task_type})")
                print(f"🔄 自动触发 if_next_step...")
                
                # Import and call if_next_step
                from agent.next_step_agent import if_next_step
                next_step_result = if_next_step()
                
                print(f"✅ TaskPickAgent: if_next_step 执行完成")
                print(f"   结果: {next_step_result.get('action', 'unknown')}")
                
                return next_step_result
            else:
                print(f"ℹ️ TaskPickAgent: 配置不完整，不触发 if_next_step")
                print(f"   model_name: {'有' if has_model_name else '无'}")
                print(f"   task_type: {'有' if has_task_type else '无'}")
                return None
                
        except Exception as e:
            print(f"❌ TaskPickAgent: 检查并触发 if_next_step 时出错: {e}")
            return None


def analyze_user_input_for_task_type(user_input: str) -> Dict[str, Any]:
    """
    Global function to analyze user input and match to task type
    
    Args:
        user_input (str): User's input text
        
    Returns:
        Dict containing analysis results
    """
    agent = TaskPickAgent()
    return agent.analyze_user_input(user_input)


def get_task_pick_agent() -> TaskPickAgent:
    """
    Get a TaskPickAgent instance
    
    Returns:
        TaskPickAgent: TaskPickAgent instance
    """
    return TaskPickAgent()


# Example usage and testing
if __name__ == "__main__":
    # Test the TaskPickAgent
    agent = TaskPickAgent()
    
    # Test cases
    test_inputs = [
        "我想进行基因敲除分析",
        "请帮我做通量平衡分析",
        "需要表型预测",
        "分析代谢途径",
        "进行进化分析",
        "约束基础分析",
        "今天天气怎么样",  # Should not match
        "分析基因表达",    # Should not match
    ]
    
    print("🧬 TaskPickAgent 测试")
    print("=" * 60)
    
    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n📋 测试 {i}: '{test_input}'")
        result = agent.analyze_user_input(test_input)
        
        if result['success']:
            if result['matched_task_type']:
                print(f"   ✅ 匹配成功: {result['matched_task_type']}")
                print(f"   📝 分析类型: {agent.analysis_types.get(result['matched_task_type'], 'Unknown')}")
            else:
                print(f"   ❌ 未匹配到分析类型")
            print(f"   🔄 bio_task已更新: {result['bio_task_updated']}")
        else:
            print(f"   💥 分析失败: {result.get('error', 'Unknown error')}")
    
    print("\n✅ 测试完成！")
