import os
import requests
from typing import List, Dict, Any, Union
import mimetypes
import json

class UnstructuredAPIClient:
    """直接调用Unstructured API的客户端"""
    
    def __init__(
        self,
        api_key: str = None,
        api_url: str = "https://api.unstructuredapp.io/general/v0/general",
    ):
        """
        初始化API客户端
        
        Args:
            api_key: Unstructured API密钥
            api_url: API端点URL
        """
        self.api_key = api_key or os.getenv("UNSTRUCTURED_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set UNSTRUCTURED_API_KEY env variable or pass api_key")
        self.api_url = api_url

    def _get_file_metadata(self, file_path: str) -> Dict[str, str]:
        """获取文件的元数据"""
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        return {
            'filename': os.path.basename(file_path),
            'content-type': content_type
        }

    def process_file(
        self,
        file_path: str,
        strategy: str = "hi_res",
        include_page_breaks: bool = True,
        include_metadata: bool = True,
        include_coords: bool = True,
        ocr_languages: List[str] = None,
        output_format: str = "application/json",
        **kwargs
    ) -> List[Dict]:
        """
        处理单个文件
        
        Args:
            file_path: 要处理的文件路径
            strategy: 处理策略 ('hi_res' or 'fast')
            include_page_breaks: 是否包含页面分隔
            include_metadata: 是否包含元数据
            include_coords: 是否包含坐标信息
            ocr_languages: OCR语言列表
            output_format: 输出格式 ('application/json' or 'text/csv')
            **kwargs: 其他API参数
        
        Returns:
            List[Dict]: API返回的处理结果
        """
        # 准备请求头
        headers = {
            'Accept': 'application/json',
            'unstructured-api-key': self.api_key
        }

        # 准备文件
        files = {
            'files': (
                os.path.basename(file_path),
                open(file_path, 'rb'),
                self._get_file_metadata(file_path)['content-type']
            )
        }

        # 准备参数
        data = {
            'strategy': strategy,
            'include_page_breaks': str(include_page_breaks).lower(),
            'include_metadata': str(include_metadata).lower(),
            'include_coords': str(include_coords).lower(),
            'output_format': output_format,
        }

        # 添加OCR语言
        if ocr_languages:
            data['ocr_languages'] = ','.join(ocr_languages)

        # 添加其他参数
        data.update(kwargs)

        try:
            # 发送请求
            response = requests.post(
                self.api_url,
                headers=headers,
                files=files,
                data=data
            )
            
            # 检查响应
            response.raise_for_status()
            
            # 返回结果
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API调用失败: {str(e)}")
            if response is not None:
                print(f"响应内容: {response.text}")
            raise
        finally:
            # 关闭文件
            files['files'][1].close()

    def process_elements(
        self,
        file_path: str,
        **kwargs
    ) -> List[Dict]:
        """处理文件并返回元素列表"""
        return self.process_file(
            file_path,
            output_format="application/json",
            **kwargs
        )

# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = UnstructuredAPIClient(
        api_key="i3Ns7H1t2kA6OtBlAEgJ3MKEIbGrO0"  # 或者设置环境变量 UNSTRUCTURED_API_KEY
    )
    
    # 处理PDF文件
    file_path = "山西-en.pdf"
    try:
        # 使用hi_res策略处理文件
        elements = client.process_elements(
            file_path,
            strategy="hi_res",
            include_coords=True,
            ocr_languages=['eng', 'chi_sim']  # 支持英文和简体中文
        )
        
        # 打印结果
        print(f"找到 {len(elements)} 个元素")
        
        # 打印第一个元素的信息
        if elements:
            first_element = elements[0]
            print("\n第一个元素信息:")
            print(json.dumps(first_element, indent=2))
            
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
