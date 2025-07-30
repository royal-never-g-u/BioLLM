from langchain.chat_models import init_chat_model
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from config import API_KEY, BASE_URL, MODEL_NAME
import os
import json
import re


class VirtualCommandAgent:
    def __init__(self):
        self.llm = init_chat_model(
            MODEL_NAME,
            model_provider="openai",
            api_key=API_KEY,
            base_url=BASE_URL
        )
        self.virtual_commands = self._load_virtual_commands()
        
        # Load the system prompt for command matching
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/virtual_command_prompt.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read().strip()

    def _load_virtual_commands(self):
        """Load all virtual commands from the VirtualCommands directory."""
        virtual_commands = {}
        commands_dir = os.path.join(os.path.dirname(__file__), '../prompts/VirtualCommands')
        
        if not os.path.exists(commands_dir):
            print(f"Warning: VirtualCommands directory not found at {commands_dir}")
            return virtual_commands
        
        for filename in os.listdir(commands_dir):
            if filename.endswith('.txt'):
                command_name = filename[:-4]  # Remove .txt extension
                file_path = os.path.join(commands_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    commands = [line.strip() for line in f.readlines() if line.strip()]
                    virtual_commands[command_name] = commands
        
        return virtual_commands

    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call the LLM with the given prompt."""
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessagePromptTemplate.from_template(system_prompt))
            messages.append(HumanMessagePromptTemplate.from_template("{input}"))
            
            chat_prompt = ChatPromptTemplate.from_messages(messages)
            full_prompt = chat_prompt.format_prompt(input=prompt)
            result = self.llm.invoke(full_prompt.to_messages())
            
            # Handle different response formats
            if hasattr(result, 'content'):
                return result.content
            elif hasattr(result, 'text'):
                return result.text
            elif isinstance(result, str):
                return result
            else:
                return str(result)
        except Exception as e:
            # Return a default response instead of raising exception
            return "LLM call failed, using fallback matching"

    def _extract_json_from_response(self, response: str) -> dict:
        """Extract JSON from LLM response, handling various formats."""
        # Clean the response
        response = response.strip()
        
        # Try to find JSON in the response with a more flexible pattern
        json_pattern = r'\{[^{}]*"matched"[^{}]*\}'
        json_match = re.search(json_pattern, response, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group(0)
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON object in the response
        try:
            # Look for the start and end of JSON
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end+1]
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # If no JSON found, try to parse the entire response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    def _calculate_semantic_similarity(self, user_input: str, command: str) -> float:
        """Calculate semantic similarity between user input and command."""
        user_input_lower = user_input.lower()
        command_lower = command.lower()
        
        # Check for exact substring matches first
        if command_lower in user_input_lower:
            return 0.8  # High confidence for substring matches
        
        user_words = set(user_input_lower.split())
        command_words = set(command_lower.split())
        
        # Calculate Jaccard similarity
        intersection = len(user_words.intersection(command_words))
        union = len(user_words.union(command_words))
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # Boost similarity for key terms
        key_terms = ['model', 'simulation', 'experiment', 'choose', 'select', 'pick', 'use', 'want']
        user_key_terms = [word for word in user_words if word in key_terms]
        command_key_terms = [word for word in command_words if word in key_terms]
        
        if user_key_terms and command_key_terms:
            key_term_overlap = len(set(user_key_terms).intersection(set(command_key_terms)))
            if key_term_overlap > 0:
                jaccard_similarity += 0.3  # Increased boost for key term matches
        
        # Additional boost for "use" and "want" patterns
        if 'use' in user_words and 'model' in command_words:
            jaccard_similarity += 0.2
        if 'want' in user_words and 'model' in command_words:
            jaccard_similarity += 0.2
        
        return min(1.0, jaccard_similarity)

    def match_command(self, user_input: str) -> dict:
        """
        Match user input against virtual commands defined in VirtualCommands folder.
        
        Returns:
            dict: {
                'matched': bool,
                'command_name': str or None,  # The filename without .txt extension
                'confidence': float or None,
                'reasoning': str
            }
        """
        if not self.virtual_commands:
            return {
                'matched': False,
                'command_name': None,
                'confidence': 0.0,
                'reasoning': 'No virtual commands loaded'
            }
        
        # Prepare the command list for the LLM
        command_list = []
        for command_name, commands in self.virtual_commands.items():
            for command in commands:
                command_list.append(f"'{command}' -> {command_name}")
        
        commands_text = "\n".join(command_list)
        
        # Create the prompt for command matching
        prompt = f"""
User Input: "{user_input}"

Available Virtual Commands (filename -> commands):
{commands_text}

Please analyze if the user input matches any of the virtual commands above. Consider semantic similarity, not just exact matches.
"""
        
        try:
            response = self._call_llm(prompt, system_prompt=self.system_prompt)
            
            # Try to parse the response as JSON
            result = self._extract_json_from_response(response)
            
            if result and isinstance(result, dict):
                return {
                    'matched': result.get('matched', False),
                    'command_name': result.get('command_name'),
                    'confidence': result.get('confidence', 0.0),
                    'reasoning': result.get('reasoning', 'No reasoning provided')
                }
            else:
                # If JSON parsing fails, use fallback semantic matching
                return self._fallback_semantic_matching(user_input, response)
                
        except Exception as e:
            # Use fallback semantic matching when LLM fails
            return self._fallback_semantic_matching(user_input, f"LLM error: {str(e)}")

    def _fallback_semantic_matching(self, user_input: str, llm_response: str) -> dict:
        """Fallback semantic matching when LLM JSON parsing fails."""
        best_match = None
        best_confidence = 0.0
        best_reasoning = ""
        
        for command_name, commands in self.virtual_commands.items():
            for command in commands:
                similarity = self._calculate_semantic_similarity(user_input, command)
                
                if similarity > best_confidence:
                    best_confidence = similarity
                    best_match = command_name
                    best_reasoning = f"Semantic similarity between '{user_input}' and '{command}': {similarity:.2f}"
        
        # Determine if it's a match based on confidence threshold
        is_matched = best_confidence >= 0.5  # Lower threshold for fallback
        
        return {
            'matched': is_matched,
            'command_name': best_match if is_matched else None,
            'confidence': best_confidence,
            'reasoning': f"Fallback matching: {best_reasoning}. LLM response parsing failed: {llm_response[:100]}..."
        }

    def _parse_text_response(self, response: str, user_input: str) -> dict:
        """Parse text response when JSON parsing fails."""
        response_lower = response.lower()
        
        # Try to find command names in the response
        matched_command = None
        for command_name in self.virtual_commands.keys():
            if command_name.lower() in response_lower:
                matched_command = command_name
                break
        
        # Determine confidence based on response content
        confidence = 0.0
        if 'match' in response_lower and 'yes' in response_lower:
            confidence = 0.8
        elif 'similar' in response_lower or 'close' in response_lower:
            confidence = 0.6
        elif 'no match' in response_lower or 'not match' in response_lower:
            confidence = 0.0
        
        return {
            'matched': matched_command is not None and confidence > 0.5,
            'command_name': matched_command,
            'confidence': confidence,
            'reasoning': response
        }

    def get_available_commands(self) -> dict:
        """Get all available virtual commands."""
        return self.virtual_commands.copy()

    def reload_commands(self):
        """Reload virtual commands from files."""
        self.virtual_commands = self._load_virtual_commands()

    def add_command(self, command_name: str, commands: list):
        """Add a new virtual command."""
        self.virtual_commands[command_name] = commands
        
        # Save to file
        commands_dir = os.path.join(os.path.dirname(__file__), '../prompts/VirtualCommands')
        file_path = os.path.join(commands_dir, f"{command_name}.txt")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            for command in commands:
                f.write(command + '\n')

    def remove_command(self, command_name: str):
        """Remove a virtual command."""
        if command_name in self.virtual_commands:
            del self.virtual_commands[command_name]
            
            # Remove file
            commands_dir = os.path.join(os.path.dirname(__file__), '../prompts/VirtualCommands')
            file_path = os.path.join(commands_dir, f"{command_name}.txt")
            
            if os.path.exists(file_path):
                os.remove(file_path) 