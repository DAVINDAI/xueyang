import os
from app.services.pdf_processor import pdf_processor_service

class DocumentConverter:
    """
    文档转换器，用于将PDF转换为Markdown
    """
    
    @staticmethod
    def pdf_to_markdown(file_path):
        """
        将PDF文件转换为Markdown格式
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            str: Markdown格式的文本
        """
        try:
            # 检查文件扩展名
            ext = os.path.splitext(file_path)[1].lower()
            if ext != '.pdf':
                return None
            
            # 读取PDF文件并提取文本
            with open(file_path, 'rb') as f:
                content = f.read()
            text = pdf_processor_service.extract_text(content)
            
            # 生成Markdown格式
            if text:
                # 简单的Markdown转换
                # 可以根据需要添加更复杂的格式处理
                markdown = f"# PDF文档内容\n\n{text}"
                return markdown
            return None
            
        except Exception as e:
            print(f"PDF转Markdown失败: {e}")
            return None

# 创建全局DocumentConverter服务实例
document_converter_service = DocumentConverter()