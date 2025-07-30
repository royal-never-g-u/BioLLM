import subprocess
import os

class CodeExecutor:
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
        # 再执行py文件
        if py_path and os.path.exists(py_path):
            try:
                result = subprocess.run(["python3", py_path], capture_output=True, text=True, timeout=30)
                output += f"[Python Output]:\n{result.stdout}{result.stderr}\n"
            except Exception as e:
                output += f"[Python Error]: {e}\n"
        if not output:
            output = "Could not find corresponding command or code file, or the file is empty."
        return output 