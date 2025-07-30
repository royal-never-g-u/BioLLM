import requests
import warnings
import sys

# 显示所有警告
warnings.filterwarnings("always")

try:
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"ERROR: beautifulsoup4 not installed. Error: {e}")
    print("Please run: pip install beautifulsoup4")
    sys.exit(1)

import os
import re
from urllib.parse import urljoin, urlparse
import time

class DownloadTool:
    def __init__(self):
        self.base_url = "http://bigg.ucsd.edu/models/"
        self.session = requests.Session()
        # 设置请求头，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def check_model_url(self, model_name: str) -> bool:
        """
        检查模型URL是否有效
        
        Args:
            model_name: 模型名称
            
        Returns:
            bool: URL是否有效
        """
        url = f"{self.base_url}{model_name}"
        try:
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"ERROR checking URL {url}: {e}")
            return False

    def find_mat_file_link(self, model_name: str) -> str:
        """
        在模型页面中查找对应的.mat文件下载链接
        
        Args:
            model_name: 模型名称
            
        Returns:
            str: .mat文件的下载链接，如果未找到则返回None
        """
        # 首先尝试直接构造.mat文件的URL
        direct_url = f"{self.base_url}static/models/{model_name}.mat"
        try:
            response = self.session.head(direct_url, timeout=5)
            if response.status_code == 200:
                print(f"Found direct .mat file URL: {direct_url}")
                return direct_url
        except Exception as e:
            print(f"Direct URL check failed for {model_name}: {e}")
        
        # 如果直接URL不存在，尝试从模型页面查找
        url = f"{self.base_url}{model_name}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找所有a标签
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().strip()
                
                # 检查是否是我们要找的.mat文件链接
                if text == f"{model_name}.mat" or href.endswith(f"{model_name}.mat"):
                    # 如果是相对链接，转换为绝对链接
                    if href.startswith('/'):
                        return urljoin(self.base_url, href)
                    elif href.startswith('http'):
                        return href
                    else:
                        return urljoin(url, href)
            
            print(f"No .mat file link found on page for {model_name}")
            return None
            
        except Exception as e:
            print(f"ERROR finding .mat file link for {model_name}: {e}")
            return None

    def download_mat_file(self, model_name: str, download_dir: str = None) -> dict:
        """
        下载模型的.mat文件
        
        Args:
            model_name: 模型名称
            download_dir: 下载目录（如果为None，使用项目根目录下的downloads文件夹）
            
        Returns:
            dict: 包含下载结果的字典
        """
        # 如果没有指定下载目录，使用项目根目录下的downloads文件夹
        if download_dir is None:
            # 使用与ModelAnalyzerAgent相同的路径检测逻辑
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_file_dir)  # BioLLM directory
            
            possible_paths = [
                os.path.join(project_root, "downloads"),     # From BioLLM/agent/
                os.path.join(os.path.dirname(project_root), "downloads"),  # From BioLLM/BioLLM/
                "../downloads",                              # From BioLLM/BioLLM/
                "../../downloads",                           # From BioLLM/agent/
                "downloads",                                 # From project root
                "./downloads",                               # From current directory
            ]
            
            download_dir = None
            for path in possible_paths:
                if os.path.exists(path):
                    # Verify this is the correct downloads directory by checking for .mat files
                    try:
                        files = os.listdir(path)
                        if any(f.endswith('.mat') for f in files):
                            download_dir = path
                            break
                    except:
                        continue
            
            if download_dir is None:
                # Fallback to relative path
                download_dir = "../downloads"
        
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        # 检查URL是否有效
        if not self.check_model_url(model_name):
            return {
                'success': False,
                'message': f"Model URL is not accessible: {self.base_url}{model_name}",
                'file_path': None
            }
        
        # 查找.mat文件链接
        mat_file_url = self.find_mat_file_link(model_name)
        if not mat_file_url:
            return {
                'success': False,
                'message': f"No .mat file found for model: {model_name}",
                'file_path': None
            }
        
        # 下载文件
        try:
            print(f"Downloading {model_name}.mat from {mat_file_url}")
            response = self.session.get(mat_file_url, timeout=30)
            response.raise_for_status()
            
            # 保存文件
            file_path = os.path.join(download_dir, f"{model_name}.mat")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(file_path)
            
            return {
                'success': True,
                'message': f"Successfully downloaded {model_name}.mat ({file_size} bytes)",
                'file_path': file_path,
                'file_size': file_size
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"Error downloading {model_name}.mat: {e}",
                'file_path': None
            }

    def download_model_from_name(self, model_name: str) -> dict:
        """
        从模型名称下载对应的.mat文件
        
        Args:
            model_name: 模型名称
            
        Returns:
            dict: 下载结果
        """
        print(f"Attempting to download model: {model_name}")
        
        # 检查模型名称格式
        if not model_name or not isinstance(model_name, str):
            return {
                'success': False,
                'message': f"Invalid model name: {model_name}",
                'file_path': None
            }
        
        # 清理模型名称（移除空格等）
        model_name = model_name.strip()
        
        # 下载文件
        result = self.download_mat_file(model_name)
        
        if result['success']:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ {result['message']}")
        
        return result

    def batch_download_models(self, model_names: list, download_dir: str = None) -> dict:
        """
        批量下载多个模型文件
        
        Args:
            model_names: 模型名称列表
            download_dir: 下载目录（如果为None，使用项目根目录下的downloads文件夹）
            
        Returns:
            dict: 批量下载结果
        """
        results = {
            'total': len(model_names),
            'successful': 0,
            'failed': 0,
            'results': []
        }
        
        for i, model_name in enumerate(model_names, 1):
            print(f"\n[{i}/{len(model_names)}] Processing model: {model_name}")
            result = self.download_model_from_name(model_name)
            results['results'].append({
                'model_name': model_name,
                'result': result
            })
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
            
            # 添加延迟避免过于频繁的请求
            time.sleep(1)
        
        print(f"\nBatch download completed: {results['successful']} successful, {results['failed']} failed")
        return results 