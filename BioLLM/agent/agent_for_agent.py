import os
import re
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from config import API_KEY, BASE_URL, MODEL_NAME

class AgentForAgent:
    """
    Agent for Agent - 智能判断用户输入是否与生物研究相关
    在第三优先级后、第四优先级前执行
    """
    
    def __init__(self):
        self.llm = init_chat_model(
            MODEL_NAME,
            model_provider="openai",
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.confidence_threshold = 0.7  # 置信度阈值
        
    def _get_prompt(self):
        """获取系统提示词"""
        return """You are an intelligent agent that determines whether user input is related to biological research and computational biology.

Your task is to analyze the user's input and determine if it's related to:
- Biological research
- Computational biology
- Bioinformatics
- Systems biology
- Metabolic modeling
- COBRA analysis
- Gene regulation
- Protein interactions
- Cell biology
- Molecular biology
- And related fields

Please respond in the following format:
CONFIDENCE: [0.0-1.0]
REASONING: [Brief explanation of your decision]

Examples:
Input: "What is FBA analysis?"
Response: CONFIDENCE: 0.95
REASONING: This is directly asking about Flux Balance Analysis, a core computational biology method.

Input: "How to cook pasta?"
Response: CONFIDENCE: 0.1
REASONING: This is about cooking, not biological research.

Input: "Tell me about E. coli metabolism"
Response: CONFIDENCE: 0.9
REASONING: This is asking about bacterial metabolism, which is a key topic in systems biology and metabolic modeling.

Input: "What's the weather like?"
Response: CONFIDENCE: 0.05
REASONING: This is about weather, completely unrelated to biological research."""

    def _extract_confidence(self, llm_response):
        """从LLM响应中提取置信度"""
        try:
            # 查找CONFIDENCE行
            confidence_match = re.search(r'CONFIDENCE:\s*([0-9]*\.?[0-9]+)', llm_response, re.IGNORECASE)
            if confidence_match:
                confidence = float(confidence_match.group(1))
                return min(max(confidence, 0.0), 1.0)  # 确保在0-1范围内
            else:
                # 如果没有找到标准格式，尝试从文本中提取数字
                numbers = re.findall(r'[0-9]*\.?[0-9]+', llm_response)
                if numbers:
                    # 取第一个数字作为置信度
                    confidence = float(numbers[0])
                    return min(max(confidence, 0.0), 1.0)
                else:
                    return 0.0
        except (ValueError, AttributeError):
            return 0.0

    def _extract_reasoning(self, llm_response):
        """从LLM响应中提取推理过程"""
        try:
            reasoning_match = re.search(r'REASONING:\s*(.+)', llm_response, re.IGNORECASE | re.DOTALL)
            if reasoning_match:
                return reasoning_match.group(1).strip()
            else:
                # 如果没有找到标准格式，返回整个响应
                return llm_response.strip()
        except AttributeError:
            return "Unable to extract reasoning"

    def check_biological_relevance(self, user_input):
        """
        检查用户输入是否与生物研究相关
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            dict: 包含以下字段的字典
                - is_relevant (bool): 是否相关
                - confidence (float): 置信度 (0.0-1.0)
                - reasoning (str): 推理过程
                - modified_input (str): 修改后的输入（如果相关）
        """
        if not user_input or not user_input.strip():
            return {
                'is_relevant': False,
                'confidence': 0.0,
                'reasoning': 'Empty input',
                'modified_input': user_input
            }
        
        try:
            # 构建消息
            system_message = SystemMessage(content=self._get_prompt())
            human_message = HumanMessage(content=f"User input: {user_input}")
            
            # 调用LLM
            response = self.llm([system_message, human_message])
            llm_response = response.content
            
            # 提取置信度和推理
            confidence = self._extract_confidence(llm_response)
            reasoning = self._extract_reasoning(llm_response)
            
            # 判断是否相关
            is_relevant = confidence >= self.confidence_threshold
            
            # 如果相关，修改输入
            modified_input = user_input
            if is_relevant:
                # 确保输入不以knowledge开头
                if not user_input.lower().strip().startswith('knowledge'):
                    modified_input = f"knowledge {user_input}"
            
            return {
                'is_relevant': is_relevant,
                'confidence': confidence,
                'reasoning': reasoning,
                'modified_input': modified_input,
                'original_input': user_input
            }
            
        except Exception as e:
            # 如果LLM调用失败，返回默认结果
            return {
                'is_relevant': False,
                'confidence': 0.0,
                'reasoning': f'Error in LLM processing: {str(e)}',
                'modified_input': user_input,
                'original_input': user_input
            }

    def run(self, user_input):
        """
        运行agent for agent
        
        Args:
            user_input (str): 用户输入
            
        Returns:
            dict: 处理结果
        """
        return self.check_biological_relevance(user_input)

    def set_confidence_threshold(self, threshold):
        """
        设置置信度阈值
        
        Args:
            threshold (float): 新的阈值 (0.0-1.0)
        """
        self.confidence_threshold = min(max(threshold, 0.0), 1.0)

    def get_confidence_threshold(self):
        """
        获取当前置信度阈值
        
        Returns:
            float: 当前阈值
        """
        return self.confidence_threshold
