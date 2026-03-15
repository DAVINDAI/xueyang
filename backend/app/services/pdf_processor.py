import PyPDF2
import io
from typing import Optional

class PDFProcessor:
    """
    PDF文件处理器，用于提取PDF中的文本内容
    """
    
    @staticmethod
    def extract_text(file_content: bytes) -> Optional[str]:
        """
        从PDF文件中提取文本
        
        Args:
            file_content: PDF文件的字节内容
            
        Returns:
            str: 提取的文本内容，如果解析失败则返回None
        """
        try:
            # 将字节内容转换为文件流
            pdf_file = io.BytesIO(file_content)
            
            # 创建PDF阅读器
            reader = PyPDF2.PdfReader(pdf_file)
            
            # 提取所有页面的文本
            text = ""
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip()
            
        except Exception as e:
            print(f"PDF解析失败: {e}")
            return None
    
    @staticmethod
    def validate_pdf(file_content: bytes) -> bool:
        """
        验证是否为有效的PDF文件
        
        Args:
            file_content: 文件的字节内容
            
        Returns:
            bool: 是否为有效的PDF文件
        """
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PyPDF2.PdfReader(pdf_file)
            return len(reader.pages) > 0
        except:
            return False

# 创建全局PDFProcessor服务实例
pdf_processor_service = PDFProcessor()
