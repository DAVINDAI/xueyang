from pymupdf4llm import to_markdown, use_layout
from typing import Optional
import io
from dotenv import load_dotenv

# 确保在初始化之前加载环境变量
load_dotenv()

# 禁用布局分析以避免表格检测时的 ONNXRuntimeError
use_layout(False)

class PDFProcessor:
    """
    PDF文件处理器，用于提取PDF中的文本内容并转换为Markdown格式
    """
    
    @staticmethod
    def extract_text(file_content: bytes) -> Optional[str]:
        """
        从PDF文件中提取文本并转换为Markdown格式
        
        Args:
            file_content: PDF文件的字节内容
            
        Returns:
            str: 提取的Markdown文本内容，如果解析失败则返回None
        """
        try:
            # 使用PyMuPDF4LLM将PDF转换为Markdown
            # 创建文件对象
            pdf_file = io.BytesIO(file_content)
            
            # 转换为Markdown
            markdown_content = to_markdown(pdf_file)
            
            return markdown_content.strip()
                
        except Exception as e:
            print(f"PDF解析失败: {e}")
            import traceback
            print(f"堆栈追踪: {traceback.format_exc()}")
            return None

    @staticmethod
    def _load_documents(file_path: str) -> Optional[list]:
        """
        加载PDF文档，处理表格检测错误
        
        Args:
            file_path: PDF文件路径
            
        Returns:
            list: 文档对象列表，如果加载失败则返回None
        """
        try:
            import pymupdf4llm
            
            # 使用LlamaMarkdownReader加载文档
            # 捕获表格检测错误，确保PDF处理能继续进行
            try:
                llama_reader = pymupdf4llm.LlamaMarkdownReader()
                documents = llama_reader.load_data(file_path)
                print(f"LlamaMarkdownReader加载成功，页码数量: {len(documents)}")
                # 为每个文档添加文件名元数据
                file_name = os.path.basename(file_path)
                for doc in documents:
                    if "file_name" not in doc.metadata:
                        doc.metadata["file_name"] = file_name
                    if "file_path" not in doc.metadata:
                        doc.metadata["file_path"] = file_path
                return documents
            except Exception as e:
                print(f"LlamaMarkdownReader加载失败，尝试使用to_markdown方法: {e}")
                # 尝试使用to_markdown方法作为备选方案
                with open(file_path, 'rb') as f:
                    pdf_content = f.read()
                markdown_content = to_markdown(pdf_content)
                # 创建简单的文档对象，添加元数据
                from llama_index.core import Document
                file_name = os.path.basename(file_path)
                documents = [Document(
                    text=markdown_content,
                    metadata={
                        "file_name": file_name,
                        "file_path": file_path,
                        "page": 1
                    }
                )]
                return documents
        except Exception as e:
            print(f"文档加载失败: {e}")
            import traceback
            print(f"堆栈追踪: {traceback.format_exc()}")
            return None
    
    @staticmethod
    def pdf_to_markdown_with_pages(file_path: str = None, documents = None) -> Optional[str]:
        """
        将PDF文件转换为Markdown格式，使用LlamaMarkdownReader处理
        
        Args:
            file_path: PDF文件路径（当documents为None时使用）
            documents: 已加载的文档对象列表（可选）
            
        Returns:
            str: Markdown内容，如果转换失败则返回None
        """
        try:
            # 如果没有提供文档对象，则加载文档
            if documents is None:
                documents = PDFProcessor._load_documents(file_path)
                if documents is None:
                    return None
            
            # 构建Markdown内容
            markdown_content = []
            for doc in documents:
                markdown_content.append(doc.text)
            
            return "\n\n".join(markdown_content)
                
        except Exception as e:
            print(f"PDF转换失败: {e}")
            import traceback
            print(f"堆栈追踪: {traceback.format_exc()}")
            return None
    
    @staticmethod
    def process_pdf_with_llamaindex(file_path: str, collection_name: str = "law_documents") -> Optional[str]:
        """
        处理PDF文件，转换为Markdown并与LlamaIndex集成，使用Chroma数据库
        
        Args:
            file_path: PDF文件路径
            collection_name: Chroma数据库集合名称
            
        Returns:
            str: 处理结果信息，如果处理失败则返回None
        """
        try:
            from llama_index.core import VectorStoreIndex
            from llama_index.vector_stores.chroma import ChromaVectorStore
            import chromadb
            import pymupdf4llm
            
            # 构建持久化存储路径
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "chroma_law"
            )
            os.makedirs(data_dir, exist_ok=True)
            
            # 创建持久化Chroma客户端
            chroma_client = chromadb.PersistentClient(path=data_dir)
            
            # 获取或创建集合
            collection = chroma_client.get_or_create_collection(name=collection_name)
            
            # 检查文档是否已经存在（通过文件路径）
            file_name = os.path.basename(file_path)
            existing_docs = collection.get(where={"file_path": file_path})
            if existing_docs and existing_docs['ids']:
                return f"文档 {file_name} 已经存在于数据库中，跳过处理"
            
            # 创建向量存储
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # 使用_load_documents方法加载PDF文件
            documents = PDFProcessor._load_documents(file_path)
            if documents is None:
                return None
            
            # 导入必要的模块
            from llama_index.core import Settings, StorageContext
            from llama_index.core.node_parser import SentenceSplitter
            # 创建嵌入模型（优先使用 DashScope 远程嵌入模型）
            import os
            api_key = os.getenv("DASHSCOPE_API_KEY")
            
            if not api_key:
                logger.warning("DASHSCOPE_API_KEY not found, please set it in environment variables")
                return None
                
            from langchain_community.embeddings import DashScopeEmbeddings
            from llama_index.embeddings.langchain import LangchainEmbedding
            langchain_embedding = DashScopeEmbeddings(model="text-embedding-v3", dashscope_api_key=api_key)
            embed_model = LangchainEmbedding(langchain_embedding)
            
            # 创建节点解析器
            node_parser = SentenceSplitter(
                separator=" ",
                chunk_size=512,
                chunk_overlap=128
            )
            
            # 设置全局配置
            Settings.embed_model = embed_model
            Settings.node_parser = node_parser
            
            # 创建存储上下文
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # 创建索引
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                embed_model=embed_model,
                transformations=[node_parser],
                show_progress=True
            )
            
            # 保存索引
            index.storage_context.persist()
            
            # 生成Markdown内容
            # 直接使用pdf_to_markdown_with_pages方法处理所有情况
            markdown_content = PDFProcessor.pdf_to_markdown_with_pages(documents=documents)
            
            if markdown_content:
                # 保存Markdown文件
                markdown_path = file_path.rsplit('.', 1)[0] + '.md'
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                return f"PDF处理完成，已保存到Chroma数据库和Markdown文件: {markdown_path}"
            else:
                return "PDF处理完成，已保存到Chroma数据库，但Markdown转换失败"
                
        except Exception as e:
            print(f"PDF处理失败: {e}")
            import traceback
            print(f"堆栈追踪: {traceback.format_exc()}")
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
            # 使用PyMuPDF4LLM尝试转换
            pdf_file = io.BytesIO(file_content)
            markdown_content = to_markdown(pdf_file)
            return len(markdown_content) > 0
        except:
            return False

# 创建全局PDFProcessor服务实例
pdf_processor_service = PDFProcessor()
