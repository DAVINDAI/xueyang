import os
import logging
from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, Document, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from app.services.db import get_chat_sessions, get_chat_messages

# 数据存储基础路径
data_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LlamaIndexService:
    def __init__(self, visitor_id: str = "default"):
        self.visitor_id = visitor_id
        # 使用绝对路径存储向量数据，与数据库路径保持一致
        if not visitor_id or visitor_id == "default":
            self.chroma_persist_dir = os.path.join(data_base_path, "chroma")
        else:
            self.chroma_persist_dir = os.path.join(data_base_path, visitor_id, "chroma")
        self.index = None
        self.embed_model = None
        self._initialize_components()
    
    def _initialize_components(self):
        try:
            os.makedirs(self.chroma_persist_dir, exist_ok=True)
            
            chroma_client = chromadb.PersistentClient(path=self.chroma_persist_dir)
            chroma_collection = chroma_client.get_or_create_collection("chat_history")
            
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                logger.warning("DASHSCOPE_API_KEY not found, please set it in environment variables")
                # 可以考虑添加备用方案，或者抛出异常
                raise Exception("DASHSCOPE_API_KEY is required for embedding model")
            else:
                # 使用DashScope远程模型
                from langchain_community.embeddings import DashScopeEmbeddings
                from llama_index.embeddings.langchain import LangchainEmbedding
                langchain_embedding = DashScopeEmbeddings(
                    model="text-embedding-v1", dashscope_api_key=api_key
                )
                self.embed_model = LangchainEmbedding(langchain_embedding)
            
            self.node_parser = SentenceSplitter(
                separator=" ",
                chunk_size=512,
                chunk_overlap=128
            )
            
            # Set global embedding model to avoid conflicts
            Settings.embed_model = self.embed_model
            Settings.node_parser = self.node_parser
            
            # 自动加载已有的索引数据
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    embed_model=self.embed_model
                )
                logger.info("Loaded existing vector index")
            except Exception as e:
                logger.info(f"Creating new vector index: {e}")
                self.index = VectorStoreIndex(
                    [],
                    embed_model=self.embed_model
                )
            
            logger.info("LlamaIndex service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex service: {e}")
            raise
    
    def _extract_chat_history(self) -> List[Document]:
        documents = []
        try:
            sessions = get_chat_sessions(self.visitor_id)
            for session in sessions:
                session_id = session["id"]
                session_name = session["session_name"]
                
                messages = get_chat_messages(self.visitor_id, session_id)
                for msg in messages:
                    content = msg["content"]
                    role = msg["role"]
                    
                    doc_text = f"[{session_name}] {role}: {content}"
                    metadata = {
                        "session_id": session_id,
                        "session_name": session_name,
                        "role": role,
                        "message_id": msg["id"],
                        "created_at": msg["created_at"],
                        "visitor_id": self.visitor_id
                    }
                    
                    documents.append(Document(text=doc_text, metadata=metadata))
            
            logger.info(f"Extracted {len(documents)} documents from chat history for visitor: {self.visitor_id}")
            return documents
        except Exception as e:
            logger.error(f"Failed to extract chat history: {e}")
            return []
    
    def build_index(self, force_rebuild: bool = False):
        try:
            # 检查是否需要构建索引
            # 1. 强制重建
            # 2. 索引不存在
            # 3. 始终构建（首次初始化时）
            # 注意：由于我们在初始化时调用此方法，所以不需要检查索引是否为空
            documents = self._extract_chat_history()
            
            if not documents:
                logger.warning("No documents found to build index")
                return
            
            # 只有当有文档时才重建索引
            chroma_client = chromadb.PersistentClient(path=self.chroma_persist_dir)
            chroma_collection = chroma_client.get_or_create_collection("chat_history")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            self.index = VectorStoreIndex.from_documents(
                    documents,
                    storage_context=storage_context,
                    embed_model=self.embed_model,
                    transformations=[self.node_parser],
                    show_progress=True
                )
            
            logger.info(f"Successfully built index with {len(documents)} documents")
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise
    
    def update_index(self, session_id: int):
        try:
            # 获取当前访客的会话列表
            session = get_chat_sessions(self.visitor_id)
            target_session = next((s for s in session if s["id"] == session_id), None)
            
            if not target_session:
                logger.warning(f"Session {session_id} not found for visitor: {self.visitor_id}")
                return
            
            messages = get_chat_messages(self.visitor_id, session_id)
            documents = []
            
            for msg in messages:
                content = msg["content"]
                role = msg["role"]
                
                doc_text = f"[{target_session['session_name']}] {role}: {content}"
                metadata = {
                    "session_id": session_id,
                    "session_name": target_session["session_name"],
                    "role": role,
                    "message_id": msg["id"],
                    "created_at": msg["created_at"],
                    "visitor_id": self.visitor_id
                }
                
                documents.append(Document(text=doc_text, metadata=metadata))
            
            if documents:
                for doc in documents:
                    # 插入文档
                    self.index.insert(doc)
                
                logger.info(f"Updated index with {len(documents)} documents from session {session_id} for visitor: {self.visitor_id}")
        except Exception as e:
            logger.error(f"Failed to update index for session {session_id}: {e}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            # Only build index if it doesn't exist
            if not self.index:
                logger.info("Index not found, building index...")
                self.build_index()
            
            if not self.index:
                logger.warning("Index is still not available after build attempt")
                return []
            
            # Use retriever directly with custom embed_model to avoid OpenAI dependency
            retriever = self.index.as_retriever(
                similarity_top_k=top_k,
                embed_model=self.embed_model
            )
            
            # Retrieve nodes directly
            nodes = retriever.retrieve(query)
            
            logger.info(f"Retrieved {len(nodes)} nodes from index")
            
            results = []
            for node in nodes:
                metadata = node.metadata
                results.append({
                    "type": "semantic",
                    "title": f"{metadata.get('session_name', 'Unknown')} - {metadata.get('role', 'Unknown')}",
                    "content": node.text[:200] + "..." if len(node.text) > 200 else node.text,
                    "sessionId": metadata.get('session_id'),
                    "messageId": metadata.get('message_id'),
                    "createdAt": metadata.get('created_at'),
                    "score": node.score if hasattr(node, 'score') else None
                })
            
            logger.info(f"Found {len(results)} semantic search results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def clear_index(self):
        try:
            chroma_client = chromadb.PersistentClient(path=self.chroma_persist_dir)
            chroma_client.delete_collection("chat_history")
            
            chroma_collection = chroma_client.create_collection("chat_history")
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            self.index = VectorStoreIndex(
                [],
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            
            logger.info("Index cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear index: {e}")
            raise

# 存储不同访客的LlamaIndex服务实例
_llamaindex_services: Dict[str, LlamaIndexService] = {}

def get_llamaindex_service(visitor_id: str = "default") -> LlamaIndexService:
    global _llamaindex_services
    # 处理 visitor_id 为 None 的情况
    if visitor_id is None:
        visitor_id = "default"

    if visitor_id not in _llamaindex_services:
        _llamaindex_services[visitor_id] = LlamaIndexService(visitor_id=visitor_id)
    return _llamaindex_services[visitor_id]

# 创建默认的LlamaIndex服务实例
llamaindex_service = get_llamaindex_service()