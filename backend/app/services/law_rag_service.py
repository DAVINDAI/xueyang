"""
法律文档RAG查询服务
提供法律文档的语义搜索和问答功能，基于向量数据库和大模型
"""
import os
import logging
from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

from app.services.llm import llm_service
from app.services.law_scraper import law_scraper_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LawRAGService:
    """
    法律文档RAG查询服务类
    提供法律文档的语义搜索和问答功能
    """
    
    def __init__(self):
        """
        初始化RAG服务
        """
        self.index = None
        self.embed_model = None
        self._initialize_components()
    
    def _initialize_components(self):
        """
        初始化RAG组件
        """
        try:
            # 构建法律文档向量存储路径
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "chroma_law"
            )
            os.makedirs(data_dir, exist_ok=True)
            
            # 创建持久化Chroma客户端
            chroma_client = chromadb.PersistentClient(path=data_dir)
            
            # 获取或创建法律文档集合
            collection = chroma_client.get_or_create_collection(name="law_documents")
            
            # 创建向量存储
            vector_store = ChromaVectorStore(chroma_collection=collection)
            
            # 创建嵌入模型（使用 DashScope 远程嵌入模型）
            import os
            api_key = os.getenv("DASHSCOPE_API_KEY")
            
            if not api_key:
                logger.warning("DASHSCOPE_API_KEY not found, please set it in environment variables")
                # 这里我们继续初始化，但实际使用时可能会失败
                # 可以考虑添加备用方案
                
            from langchain_community.embeddings import DashScopeEmbeddings
            from llama_index.embeddings.langchain import LangchainEmbedding
            langchain_embedding = DashScopeEmbeddings(model="qwen3-vl-embedding", dashscope_api_key=api_key)
            self.embed_model = LangchainEmbedding(langchain_embedding)
            
            # 设置全局配置
            Settings.embed_model = self.embed_model
            
            # 创建存储上下文
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # 加载或创建索引
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    embed_model=self.embed_model
                )
                logger.info("成功加载法律文档向量索引")
            except Exception as e:
                logger.info(f"创建新的法律文档向量索引: {e}")
                self.index = VectorStoreIndex(
                    [],
                    embed_model=self.embed_model
                )
            
            logger.info("法律文档RAG服务初始化成功")
        except Exception as e:
            logger.error(f"初始化法律文档RAG服务失败: {e}")
            raise
    
    def semantic_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        语义搜索法律文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表
        """
        try:
            if not self.index:
                logger.warning("向量索引未初始化，返回空结果")
                return []
            
            # 使用检索器进行语义搜索
            retriever = self.index.as_retriever(
                similarity_top_k=top_k,
                embed_model=self.embed_model
            )
            
            # 直接检索节点
            nodes = retriever.retrieve(query)
            
            logger.info(f"语义搜索到 {len(nodes)} 个相关文档")
            
            results = []
            for node in nodes:
                metadata = node.metadata
                # 计算归一化的相似度分数（0-1范围）
                score = node.score if hasattr(node, 'score') else None
                normalized_score = None
                if score is not None:
                    # 假设 score 是余弦相似度，范围在 [-1, 1] 之间
                    # 将其归一化到 [0, 1] 范围
                    normalized_score = (score + 1) / 2
                
                results.append({
                    "type": "law_document",
                    "title": metadata.get("file_name", "未知文件名"),
                    "content": node.text[:300] + "..." if len(node.text) > 300 else node.text,
                    "filePath": metadata.get("file_path", ""),
                    "score": normalized_score,
                    "pageNumber": metadata.get("page", 1),
                    "createdAt": metadata.get("created_at", "")
                })
            
            return results
        except Exception as e:
            logger.error(f"语义搜索失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def query_with_rag(self, query: str, model_name: str = "qwen-plus", top_k: int = 3) -> Dict[str, Any]:
        """
        使用RAG技术回答法律问题
        
        Args:
            query: 查询文本
            model_name: 大模型名称
            top_k: 检索相关文档数量
            
        Returns:
            Dict[str, Any]: 包含答案和参考文档的结果
        """
        try:
            # 检索相关法律文档
            relevant_docs = self.semantic_search(query, top_k)
            
            if not relevant_docs:
                return {
                    "answer": "抱歉，没有找到相关的法律文档来回答您的问题。",
                    "references": [],
                    "query": query
                }
            
            # 构建上下文
            context = ""
            for doc in relevant_docs:
                context += f"【{doc['title']}】\n{doc['content']}\n\n"
            
            # 构建提示词
            prompt = f"""
            您是一名专业的法律咨询助手，基于以下提供的法律文档内容来回答用户的问题。

            法律文档内容：
            {context}

            用户问题：
            {query}

            要求：
            1. 基于提供的法律文档内容回答问题，不要引入外部信息
            2. 回答要准确、专业，使用法律术语
            3. 如果文档中没有直接答案，可以提供相关法律条文的引用
            4. 保持回答的简洁和清晰

            回答：
            """
            
            # 使用大模型生成回答
            try:
                answer = llm_service.chat(model_name, None, prompt, [])
            except Exception as e:
                logger.error(f"大模型调用失败: {e}")
                return {
                    "answer": "抱歉，大模型服务暂时不可用，请稍后重试。",
                    "references": relevant_docs,
                    "query": query
                }
            
            return {
                "answer": answer,
                "references": relevant_docs,
                "query": query
            }
        
        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "answer": "抱歉，查询过程中出现错误，请稍后重试。",
                "references": [],
                "query": query
            }
    
    def get_document_count(self) -> int:
        """
        获取已索引的法律文档数量
        
        Returns:
            int: 已索引的法律文档数量
        """
        try:
            # 构建法律文档向量存储路径
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "chroma_law"
            )
            
            # 创建持久化Chroma客户端
            chroma_client = chromadb.PersistentClient(path=data_dir)
            
            # 获取法律文档集合
            collection = chroma_client.get_or_create_collection(name="law_documents")
            
            return collection.count()
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return 0
    
    def refresh_index(self) -> str:
        """
        刷新法律文档索引
        
        Returns:
            str: 刷新结果信息
        """
        try:
            # 获取所有已下载的法律文档
            law_docs = law_scraper_service.get_available_law_docs()
            
            logger.info(f"找到 {len(law_docs)} 个已下载的法律文档")
            
            # 处理每个文档并更新索引
            processed_count = 0
            
            for doc in law_docs:
                file_path = doc.get("file_path")
                file_name = doc.get("filename")
                
                if not file_path or not os.path.exists(file_path):
                    logger.warning(f"文件路径无效: {file_path}")
                    continue
                
                try:
                    self._process_and_add_document(file_path, file_name)
                    processed_count += 1
                    logger.info(f"成功处理文档: {file_name}")
                except Exception as e:
                    logger.error(f"处理文档失败 {file_name}: {e}")
            
            return f"索引刷新完成，处理了 {processed_count} 个法律文档"
        
        except Exception as e:
            logger.error(f"刷新索引失败: {e}")
            return f"索引刷新失败: {str(e)}"
    
    def _process_and_add_document(self, file_path: str, file_name: str):
        """
        处理并添加单个法律文档到向量索引
        
        Args:
            file_path: 文件路径
            file_name: 文件名
        """
        try:
            from app.services.pdf_processor import pdf_processor_service
            
            # 处理PDF文件
            result = pdf_processor_service.process_pdf_with_llamaindex(
                file_path, 
                collection_name="pdf_documents"
            )
            
            if result:
                logger.info(f"文档处理结果: {result}")
            else:
                logger.warning(f"文档处理失败: {file_name}")
        
        except Exception as e:
            logger.error(f"处理文档失败 {file_name}: {e}")
            raise

# 创建全局的法律文档RAG服务实例
law_rag_service = LawRAGService()
