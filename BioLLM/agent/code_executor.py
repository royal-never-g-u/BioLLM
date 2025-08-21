import subprocess
import os
import tempfile
import uuid
import re
from datetime import datetime

class CodeExecutor:
    def __init__(self):
        # Initialize LLM for code repair
        from langchain.chat_models import init_chat_model
        from config import API_KEY, BASE_URL, MODEL_NAME
        
        self.llm = init_chat_model(
            MODEL_NAME,
            model_provider="openai",
            api_key=API_KEY,
            base_url=BASE_URL
        )
        
        # Load code repair prompt
        prompt_path = os.path.join(os.path.dirname(__file__), '../prompts/code_debugger_prompt.txt')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.debug_prompt = f.read().strip()
        except FileNotFoundError:
            # If prompt file not found, use default prompt
            self.debug_prompt = """You are a Python code debugger. When given a Python file with errors and the error message, you should:

1. Analyze the error message carefully
2. Identify the root cause of the problem
3. Provide a corrected version of the Python code
4. Ensure the corrected code is complete and runnable
5. Add comments explaining what was fixed

Please return ONLY the corrected Python code without any additional explanations or markdown formatting."""

    def _detect_missing_dependencies(self, error_message: str) -> list[str]:
        """
        从错误信息中检测缺失的依赖包
        
        Args:
            error_message: Python错误信息
            
        Returns:
            list[str]: 缺失的依赖包列表
        """
        missing_packages = []
        
        # 常见的ModuleNotFoundError模式
        module_not_found_patterns = [
            r"No module named ['\"]([^'\"]+)['\"]",
            r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
            r"ImportError: No module named ['\"]([^'\"]+)['\"]"
        ]
        
        # 检查ModuleNotFoundError
        for pattern in module_not_found_patterns:
            matches = re.findall(pattern, error_message, re.IGNORECASE)
            for match in matches:
                # 过滤掉标准库模块
                if not self._is_standard_library_module(match):
                    missing_packages.append(match)
        
        # 检查ImportError的其他模式
        import_error_patterns = [
            r"ImportError: cannot import name ['\"]([^'\"]+)['\"] from ['\"]([^'\"]+)['\"]",
            r"ImportError: cannot import name ['\"]([^'\"]+)['\"]"
        ]
        
        for pattern in import_error_patterns:
            matches = re.findall(pattern, error_message, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 如果是元组，取第一个元素（通常是模块名）
                    module_name = match[0]
                else:
                    module_name = match
                if not self._is_standard_library_module(module_name):
                    missing_packages.append(module_name)
        
        # 去重并返回
        return list(set(missing_packages))

    def _is_standard_library_module(self, module_name: str) -> bool:
        """
        检查是否为Python标准库模块
        
        Args:
            module_name: 模块名
            
        Returns:
            bool: 是否为标准库模块
        """
        import sys
        
        # 常见的标准库模块列表
        standard_modules = {
            'os', 'sys', 're', 'json', 'datetime', 'time', 'random', 'math',
            'collections', 'itertools', 'functools', 'pathlib', 'tempfile',
            'subprocess', 'threading', 'multiprocessing', 'asyncio', 'logging',
            'argparse', 'configparser', 'csv', 'pickle', 'sqlite3', 'urllib',
            'http', 'socket', 'ssl', 'hashlib', 'base64', 'zlib', 'gzip',
            'shutil', 'glob', 'fnmatch', 'stat', 'pwd', 'grp', 'pipes',
            'signal', 'select', 'fcntl', 'termios', 'tty', 'pty', 'pwd',
            'crypt', 'spwd', 'grp', 'pwd', 'crypt', 'spwd', 'grp', 'pwd',
            'crypt', 'spwd', 'grp', 'pwd', 'crypt', 'spwd', 'grp', 'pwd'
        }
        
        # 检查是否在标准库模块列表中
        if module_name in standard_modules:
            return True
        
        # 尝试导入模块，如果能导入且路径包含标准库路径，则为标准库
        try:
            import importlib.util
            spec = importlib.util.find_spec(module_name)
            if spec and spec.origin:
                # 检查模块路径是否在标准库路径中
                stdlib_paths = [os.path.dirname(os.__file__)]
                for stdlib_path in stdlib_paths:
                    if stdlib_path in spec.origin:
                        return True
        except:
            pass
        
        return False

    def _get_package_name(self, module_name: str) -> str:
        """
        根据模块名获取对应的pip包名
        
        Args:
            module_name: 模块名
            
        Returns:
            str: pip包名
        """
        # 常见的模块名到包名的映射
        module_to_package = {
            'numpy': 'numpy',
            'pandas': 'pandas',
            'matplotlib': 'matplotlib',
            'seaborn': 'seaborn',
            'scipy': 'scipy',
            'sklearn': 'scikit-learn',
            'tensorflow': 'tensorflow',
            'torch': 'torch',
            'keras': 'keras',
            'plotly': 'plotly',
            'bokeh': 'bokeh',
            'altair': 'altair',
            'cobra': 'cobra',
            'cobrapy': 'cobrapy',
            'libsbml': 'python-libsbml',
            'libsbml': 'libsbml',
            'escher': 'escher',
            'metabotools': 'metabotools',
            'optlang': 'optlang',
            'pulp': 'pulp',
            'gurobipy': 'gurobipy',
            'cplex': 'cplex',
            'glpk': 'python-glpk',
            'glpk': 'glpk',
            'openpyxl': 'openpyxl',
            'xlsxwriter': 'xlsxwriter',
            'xlrd': 'xlrd',
            'xlwt': 'xlwt',
            'requests': 'requests',
            'urllib3': 'urllib3',
            'beautifulsoup4': 'beautifulsoup4',
            'bs4': 'beautifulsoup4',
            'lxml': 'lxml',
            'html5lib': 'html5lib',
            'selenium': 'selenium',
            'flask': 'flask',
            'django': 'django',
            'fastapi': 'fastapi',
            'uvicorn': 'uvicorn',
            'sqlalchemy': 'sqlalchemy',
            'psycopg2': 'psycopg2-binary',
            'pymongo': 'pymongo',
            'redis': 'redis',
            'celery': 'celery',
            'jinja2': 'jinja2',
            'markdown': 'markdown',
            'pillow': 'pillow',
            'opencv': 'opencv-python',
            'cv2': 'opencv-python',
            'imageio': 'imageio',
            'scikit-image': 'scikit-image',
            'nltk': 'nltk',
            'spacy': 'spacy',
            'gensim': 'gensim',
            'transformers': 'transformers',
            'torch': 'torch',
            'tensorflow': 'tensorflow',
            'jax': 'jax',
            'jaxlib': 'jaxlib',
            'langchain': 'langchain',
            'openai': 'openai',
            'anthropic': 'anthropic',
            'tiktoken': 'tiktoken',
            'chromadb': 'chromadb',
            'faiss': 'faiss-cpu',
            'faiss-gpu': 'faiss-gpu',
            'pinecone': 'pinecone-client',
            'weaviate': 'weaviate-client',
            'qdrant': 'qdrant-client',
            'milvus': 'pymilvus',
            'elasticsearch': 'elasticsearch',
            'pymongo': 'pymongo',
            'redis': 'redis',
            'sqlite3': None,  # 标准库
            'json': None,     # 标准库
            'csv': None,      # 标准库
            'pickle': None,   # 标准库
            'xml': None,      # 标准库
            'html': None,     # 标准库
            'urllib': None,   # 标准库
            'http': None,     # 标准库
            'socket': None,   # 标准库
            'ssl': None,      # 标准库
            'hashlib': None,  # 标准库
            'base64': None,   # 标准库
            'zlib': None,     # 标准库
            'gzip': None,     # 标准库
            'bz2': None,      # 标准库
            'lzma': None,     # 标准库
            'zipfile': None,  # 标准库
            'tarfile': None,  # 标准库
            'shutil': None,   # 标准库
            'glob': None,     # 标准库
            'fnmatch': None,  # 标准库
            'pathlib': None,  # 标准库
            'tempfile': None, # 标准库
            'subprocess': None, # 标准库
            'threading': None, # 标准库
            'multiprocessing': None, # 标准库
            'asyncio': None,  # 标准库
            'logging': None,  # 标准库
            'argparse': None, # 标准库
            'configparser': None, # 标准库
            'datetime': None, # 标准库
            'time': None,     # 标准库
            'calendar': None, # 标准库
            'random': None,   # 标准库
            'math': None,     # 标准库
            'statistics': None, # 标准库
            'decimal': None,  # 标准库
            'fractions': None, # 标准库
            'collections': None, # 标准库
            'itertools': None, # 标准库
            'functools': None, # 标准库
            'operator': None, # 标准库
            'enum': None,     # 标准库
            'typing': None,   # 标准库
            'dataclasses': None, # 标准库
            'abc': None,      # 标准库
            'copy': None,     # 标准库
            'pprint': None,   # 标准库
            'reprlib': None,  # 标准库
            'textwrap': None, # 标准库
            'string': None,   # 标准库
            're': None,       # 标准库
            'difflib': None,  # 标准库
            'unicodedata': None, # 标准库
            'stringprep': None, # 标准库
            'readline': None, # 标准库
            'rlcompleter': None, # 标准库
        }
        
        # 如果模块名在映射中，返回对应的包名
        if module_name in module_to_package:
            return module_to_package[module_name]
        
        # 如果没有映射，通常模块名就是包名
        return module_name

    def _install_dependencies(self, packages: list[str]) -> tuple[bool, str]:
        """
        使用pip安装依赖包
        
        Args:
            packages: 要安装的包列表
            
        Returns:
            tuple[bool, str]: (是否成功, 输出信息)
        """
        if not packages:
            return True, "No packages to install"
        
        print(f"\n📦 检测到缺失的依赖包: {', '.join(packages)}")
        print("🔧 正在自动安装依赖...")
        
        output = ""
        success_count = 0
        
        for package in packages:
            pip_package = self._get_package_name(package)
            
            if pip_package is None:
                print(f"⚠️  {package} 是标准库模块，无需安装")
                continue
            
            print(f"📥 正在安装 {pip_package}...")
            
            try:
                # 使用pip安装包
                result = subprocess.run(
                    ["pip3", "install", pip_package],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2分钟超时
                )
                
                if result.returncode == 0:
                    print(f"✅ {pip_package} 安装成功")
                    output += f"[Package Install Success]: {pip_package}\n"
                    success_count += 1
                else:
                    print(f"❌ {pip_package} 安装失败: {result.stderr}")
                    output += f"[Package Install Failed]: {pip_package} - {result.stderr}\n"
                    
            except subprocess.TimeoutExpired:
                print(f"⏰ {pip_package} 安装超时")
                output += f"[Package Install Timeout]: {pip_package}\n"
            except Exception as e:
                print(f"❌ {pip_package} 安装异常: {e}")
                output += f"[Package Install Error]: {pip_package} - {e}\n"
        
        if success_count == len(packages):
            print("🎉 所有依赖包安装完成！")
            return True, output
        elif success_count > 0:
            print(f"⚠️ 部分依赖包安装成功 ({success_count}/{len(packages)})")
            return False, output
        else:
            print("❌ 所有依赖包安装失败")
            return False, output

    def _call_llm_for_debug(self, original_code: str, error_message: str) -> str:
        """
        调用LLM修复代码错误
        
        Args:
            original_code: 原始代码
            error_message: 错误信息
            
        Returns:
            str: 修复后的代码
        """
        try:
            from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
            
            # 构建提示词
            system_prompt = SystemMessagePromptTemplate.from_template(self.debug_prompt)
            human_prompt = HumanMessagePromptTemplate.from_template(
                "Original Python code:\n{code}\n\nError message:\n{error}\n\nPlease provide the corrected code:"
            )
            
            chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
            full_prompt = chat_prompt.format_prompt(code=original_code, error=error_message)
            
            result = self.llm.invoke(full_prompt.to_messages())
            output = getattr(result, "content", str(result))
            
            return output
            
        except Exception as e:
            print(f"Error calling LLM for debugging: {e}")
            return None

    def _save_debugged_code(self, original_code: str, error_message: str, debugged_code: str, py_path: str) -> str:
        """
        保存调试后的代码到Temp文件夹
        
        Args:
            original_code: 原始代码
            error_message: 错误信息
            debugged_code: 调试后的代码
            py_path: 原始Python文件路径
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 创建Temp文件夹（如果不存在）
            temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # 生成唯一的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            original_filename = os.path.basename(py_path)
            filename_without_ext = os.path.splitext(original_filename)[0]
            
            debugged_filename = f"{filename_without_ext}_debugged_{timestamp}_{unique_id}.py"
            debugged_path = os.path.join(temp_dir, debugged_filename)
            
            # 保存调试后的代码
            with open(debugged_path, 'w', encoding='utf-8') as f:
                f.write(f"# Debugged version of {original_filename}\n")
                f.write(f"# Original error: {error_message}\n")
                f.write(f"# Debugged at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Original file: {py_path}\n")
                f.write("#" * 80 + "\n\n")
                f.write(debugged_code)
            
            # 同时保存错误报告
            report_filename = f"{filename_without_ext}_error_report_{timestamp}_{unique_id}.txt"
            report_path = os.path.join(temp_dir, report_filename)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"Error Report for {original_filename}\n")
                f.write("=" * 50 + "\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Original file: {py_path}\n")
                f.write(f"Debugged file: {debugged_path}\n\n")
                f.write("Original Code:\n")
                f.write("-" * 30 + "\n")
                f.write(original_code)
                f.write("\n\nError Message:\n")
                f.write("-" * 30 + "\n")
                f.write(error_message)
                f.write("\n\nDebugged Code:\n")
                f.write("-" * 30 + "\n")
                f.write(debugged_code)
            
            return debugged_path
            
        except Exception as e:
            print(f"Error saving debugged code: {e}")
            return None

    def _execute_python_with_debug(self, py_path: str) -> tuple[str, bool]:
        """
        执行Python文件，如果出错则进行调试或安装依赖
        
        Args:
            py_path: Python文件路径
            
        Returns:
            tuple[str, bool]: (输出信息, 是否成功)
        """
        try:
            # 读取原始代码
            with open(py_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # 尝试执行Python文件
            result = subprocess.run(
                ["python3", py_path], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            output = f"[Python Output]:\n{result.stdout}"
            
            # 检查是否有错误
            if result.stderr:
                output += f"\n[Python Error]:\n{result.stderr}"
                
                # 首先检查是否是依赖缺失错误
                missing_dependencies = self._detect_missing_dependencies(result.stderr)
                
                if missing_dependencies:
                    print(f"\n🔍 检测到缺失的依赖包: {missing_dependencies}")
                    
                    # 尝试安装依赖
                    install_success, install_output = self._install_dependencies(missing_dependencies)
                    output += f"\n[Package Installation]:\n{install_output}"
                    
                    if install_success:
                        print("🔄 依赖安装完成，重新执行代码...")
                        
                        # 重新执行Python文件
                        retry_result = subprocess.run(
                            ["python3", py_path], 
                            capture_output=True, 
                            text=True, 
                            timeout=30
                        )
                        
                        output += f"\n[Retry Python Output]:\n{retry_result.stdout}"
                        
                        if retry_result.stderr:
                            output += f"\n[Retry Python Error]:\n{retry_result.stderr}"
                            
                            # 如果重试后仍有错误，进行调试
                            print(f"\n🔍 依赖安装后仍有错误，进行调试...")
                            print(f"错误信息: {retry_result.stderr}")
                            
                            debugged_code = self._call_llm_for_debug(original_code, retry_result.stderr)
                            
                            if debugged_code:
                                debugged_path = self._save_debugged_code(
                                    original_code, retry_result.stderr, debugged_code, py_path
                                )
                                
                                if debugged_path:
                                    output += f"\n\n🔧 代码已修复并保存到: {debugged_path}"
                                    output += f"\n💡 请检查修复后的代码，然后重新运行。"
                                    output += f"\n🚪 退出executor功能，返回主菜单。"
                                    return output, False
                                else:
                                    output += f"\n❌ 保存调试代码失败"
                            else:
                                output += f"\n❌ LLM调试失败"
                            
                            return output, False
                        else:
                            print("✅ 依赖安装后代码执行成功！")
                            return output, True
                    else:
                        print("❌ 依赖安装失败，进行代码调试...")
                        
                        # 依赖安装失败，进行调试
                        debugged_code = self._call_llm_for_debug(original_code, result.stderr)
                        
                        if debugged_code:
                            debugged_path = self._save_debugged_code(
                                original_code, result.stderr, debugged_code, py_path
                            )
                            
                            if debugged_path:
                                output += f"\n\n🔧 代码已修复并保存到: {debugged_path}"
                                output += f"\n💡 请检查修复后的代码，然后重新运行。"
                                output += f"\n🚪 退出executor功能，返回主菜单。"
                                return output, False
                            else:
                                output += f"\n❌ 保存调试代码失败"
                        else:
                            output += f"\n❌ LLM调试失败"
                        
                        return output, False
                else:
                    # 不是依赖错误，进行常规调试
                    print(f"\n🔍 检测到Python代码错误，正在调试...")
                    print(f"错误信息: {result.stderr}")
                    
                    # 调用LLM修复代码
                    debugged_code = self._call_llm_for_debug(original_code, result.stderr)
                    
                    if debugged_code:
                        # 保存调试后的代码
                        debugged_path = self._save_debugged_code(
                            original_code, result.stderr, debugged_code, py_path
                        )
                        
                        if debugged_path:
                            output += f"\n\n🔧 代码已修复并保存到: {debugged_path}"
                            output += f"\n💡 请检查修复后的代码，然后重新运行。"
                            output += f"\n🚪 退出executor功能，返回主菜单。"
                            
                            # 返回错误状态，让main.py知道需要退出executor
                            return output, False
                        else:
                            output += f"\n❌ 保存调试代码失败"
                    else:
                        output += f"\n❌ LLM调试失败"
                    
                    return output, False
            
            return output, True
            
        except subprocess.TimeoutExpired:
            error_msg = "Python execution timed out after 30 seconds"
            output = f"[Python Error]: {error_msg}"
            return output, False
            
        except Exception as e:
            error_msg = f"Error executing Python file: {e}"
            output = f"[Python Error]: {error_msg}"
            return output, False

    def run(self, prompt: str, memory=None) -> str:
        from agent.code_writer import CodeWriterAgent
        writer = CodeWriterAgent()
        keywords = writer.extract_keywords_ml(prompt) if prompt else None
        txt_path = os.path.join("ResultsData", f"{keywords}.txt") if keywords else None
        py_path = os.path.join("ResultsData", f"{keywords}.py") if keywords else None
        output = ""
        
        # 如果找不到对应文件，默认取第一个txt/py文件
        if not txt_path or not os.path.exists(txt_path):
            txt_files = [f for f in os.listdir("ResultsData") if f.endswith(".txt")]
            txt_path = os.path.join("ResultsData", txt_files[0]) if txt_files else None
        if not py_path or not os.path.exists(py_path):
            py_files = [f for f in os.listdir("ResultsData") if f.endswith(".py")]
            py_path = os.path.join("ResultsData", py_files[0]) if py_files else None
        
        # 先执行txt中的bash命令
        if txt_path and os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                bash_cmds = f.read().strip()
            if bash_cmds:
                try:
                    result = subprocess.run(bash_cmds, shell=True, capture_output=True, text=True, timeout=30)
                    output += f"[Bash Output]:\n{result.stdout}{result.stderr}\n"
                except Exception as e:
                    output += f"[Bash Error]: {e}\n"
        
        # 再执行py文件（带调试和依赖安装功能）
        if py_path and os.path.exists(py_path):
            py_output, py_success = self._execute_python_with_debug(py_path)
            output += py_output
            
            # 如果Python执行失败，返回特殊标记让main.py知道需要退出executor
            if not py_success:
                # 添加特殊标记，让main.py识别这是调试后的退出
                output += "\n\n[DEBUG_EXIT]"
                return output
        
        if not output:
            output = "Could not find corresponding command or code file, or the file is empty."
        
        return output 