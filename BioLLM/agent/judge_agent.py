#!/usr/bin/env python3
"""
Judge Agent - Determines if user input is a positive response
"""

import re
from typing import Union, Dict, Any
from agent.base import BaseAgent
from langchain.schema import HumanMessage, SystemMessage

class JudgeAgent(BaseAgent):
    """
    Agent for judging whether user input is a positive response
    """
    
    def __init__(self):
        self.system_prompt = """You are a response judge. Your task is to determine if the user's input indicates a positive response (agreement, consent, approval, etc.).

You should return ONLY a boolean value:
- Return "true" if the input indicates agreement, consent, approval, or positive response
- Return "false" if the input indicates disagreement, refusal, or negative response

Examples of positive responses (return "true"):
- "yes", "ok", "okay", "sure", "alright", "fine"
- "同意", "好的", "可以", "行", "没问题", "当然"
- "I agree", "That's fine", "Go ahead", "Proceed"
- "Yes, please", "Sure thing", "Absolutely", "Definitely"
- "好的", "可以", "行", "没问题", "当然", "许可", "同意"

Examples of negative responses (return "false"):
- "no", "nope", "not", "don't", "won't", "can't"
- "不", "不行", "不可以", "不同意", "拒绝"
- "I don't think so", "Not really", "I'd rather not"
- "No thanks", "I'll pass", "Maybe later"

If the input is unclear or neutral, return "false".

IMPORTANT: Respond with ONLY "true" or "false" - no other text."""

    def judge_response(self, user_input: str) -> bool:
        """
        Judge if user input is a positive response
        
        Args:
            user_input (str): User's input text
            
        Returns:
            bool: True if positive response, False otherwise
        """
        try:
            # First try simple pattern matching for common responses
            if self._simple_pattern_match(user_input):
                return True
            
            # If simple matching fails, use LLM for complex cases
            return self._llm_judge(user_input)
            
        except Exception as e:
            print(f"Error in judge_response: {e}")
            # Default to False if there's an error
            return False
    
    def _simple_pattern_match(self, user_input: str) -> bool:
        """
        Simple pattern matching for common positive responses
        """
        if not user_input:
            return False
        
        # Convert to lowercase for comparison
        input_lower = user_input.lower().strip()
        
        # Common positive responses in English
        positive_patterns = [
            r'^yes$', r'^ok$', r'^okay$', r'^sure$', r'^alright$', r'^fine$',
            r'^absolutely$', r'^definitely$', r'^certainly$', r'^of course$',
            r'^go ahead$', r'^proceed$', r'^continue$', r'^start$',
            r'^i agree$', r'^that\'s fine$', r'^sure thing$', r'^why not$'
        ]
        
        # Common positive responses in Chinese
        chinese_positive = [
            r'^同意$', r'^好的$', r'^可以$', r'^行$', r'^没问题$', r'^当然$',
            r'^许可$', r'^赞成$', r'^支持$', r'^愿意$', r'^乐意$',
            r'^好的$', r'^可以$', r'^行$', r'^没问题$', r'^当然$'
        ]
        
        # Check English patterns
        for pattern in positive_patterns:
            if re.match(pattern, input_lower):
                return True
        
        # Check Chinese patterns
        for pattern in chinese_positive:
            if re.match(pattern, input_lower):
                return True
        
        return False
    
    def _llm_judge(self, user_input: str) -> bool:
        """
        Use LLM to judge complex responses
        """
        try:
            # Create messages for LLM
            messages = [
                HumanMessage(content=f"User input: '{user_input}'\n\nIs this a positive response? Return only 'true' or 'false'.")
            ]
            
            # For now, we'll use a simple approach without external LLM
            # In a real implementation, you would call your LLM here
            # For example:
            # response = self.llm.invoke(messages)
            # result = response.content.strip().lower()
            
            # Simple fallback logic for demonstration
            result = self._fallback_judge(user_input)
            
            # Parse the result
            if result in ['true', '1', 'yes', 'ok']:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error in LLM judge: {e}")
            return False
    
    def _fallback_judge(self, user_input: str) -> str:
        """
        Fallback judge when LLM is not available
        """
        input_lower = user_input.lower().strip()
        
        # Check for negative patterns FIRST (to avoid false positives)
        negative_keywords = [
            'no', 'nope', 'not', 'don\'t', 'won\'t', 'can\'t', 'never',
            'refuse', 'reject', 'decline', 'stop', 'cancel', 'quit',
            '不', '不行', '不可以', '不同意', '拒绝', '不要', '别',
            '算了', '不用了', '免了', '拉倒', '算了', '你好', '什么', '?'
        ]
        
        for keyword in negative_keywords:
            if keyword in input_lower:
                return 'false'
        
        # More comprehensive positive patterns
        positive_keywords = [
            'yes', 'ok', 'okay', 'sure', 'alright', 'fine', 'good', 'great',
            'absolutely', 'definitely', 'certainly', 'of course', 'indeed',
            'go ahead', 'proceed', 'continue', 'start', 'begin',
            'i agree', 'that\'s fine', 'sure thing', 'why not', 'let\'s',
            '同意', '好的', '可以', '行', '没问题', '当然', '许可', '赞成',
            '支持', '愿意', '乐意', '好', '对', '是', '嗯', '嗯嗯'
        ]
        
        # Check if any positive keyword is in the input
        for keyword in positive_keywords:
            if keyword in input_lower:
                return 'true'
        
        # Default to false for unclear responses
        return 'false'
    
    def run(self, prompt: str, memory=None) -> str:
        """
        Run the judge agent (implements BaseAgent interface)
        """
        result = self.judge_response(prompt)
        return str(result).lower()
    
    def get_judgment_with_confidence(self, user_input: str) -> Dict[str, Any]:
        """
        Get judgment with confidence level
        
        Args:
            user_input (str): User's input text
            
        Returns:
            Dict containing judgment and confidence
        """
        try:
            # Simple confidence calculation based on pattern matching
            input_lower = user_input.lower().strip()
            
            # Count positive and negative indicators
            positive_count = 0
            negative_count = 0
            
            # Check positive indicators
            positive_keywords = ['yes', 'ok', 'sure', '同意', '好的', '可以']
            for keyword in positive_keywords:
                if keyword in input_lower:
                    positive_count += 1
            
            # Check negative indicators
            negative_keywords = ['no', 'not', '不', '不行', '不可以']
            for keyword in negative_keywords:
                if keyword in input_lower:
                    negative_count += 1
            
            # Calculate confidence
            total_indicators = positive_count + negative_count
            if total_indicators == 0:
                confidence = 0.5  # Neutral confidence
            else:
                confidence = max(positive_count, negative_count) / total_indicators
            
            # Get judgment
            judgment = self.judge_response(user_input)
            
            return {
                'judgment': judgment,
                'confidence': confidence,
                'positive_indicators': positive_count,
                'negative_indicators': negative_count,
                'input': user_input
            }
            
        except Exception as e:
            print(f"Error in get_judgment_with_confidence: {e}")
            return {
                'judgment': False,
                'confidence': 0.0,
                'positive_indicators': 0,
                'negative_indicators': 0,
                'input': user_input
            }

# Global instance
judge_agent = JudgeAgent()

def get_judge_agent():
    """Get the global judge agent instance"""
    return judge_agent

def judge_user_response(user_input: str) -> bool:
    """
    Convenience function to judge user response
    
    Args:
        user_input (str): User's input text
        
    Returns:
        bool: True if positive response, False otherwise
    """
    return judge_agent.judge_response(user_input)
