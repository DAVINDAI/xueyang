import os
import logging
from typing import List, Dict, Any, Optional
from llama_index.core import VectorStoreIndex, Document, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.embeddings import BaseEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from app.services.db import get_chat_sessions, get_chat_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelScopeEmbedding(BaseEmbedding):
    model_name: str = "BAAI/bge-small-zh-v1.5"
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5", **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self._load_model()
    
    def _load_model(self):
        try:
            from modelscope.models import AutoModel, AutoTokenizer
            logger.info(f"Loading ModelScope model: {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)
            logger.info("ModelScope model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load ModelScope model: {e}")
            raise
    
    def _get_query_embedding(self, query: str) -> List[float]:
        return self._get_text_embedding(query)
    
    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)
    
    def _get_text_embedding(self, text: str) -> List[float]:
        import torch
        inputs = self._tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self._model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings[0].tolist()
    
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._get_text_embedding(text) for text in texts]
    
    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)
    
    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._get_text_embedding(text) for text in texts]

class LlamaIndexService:
    def __init__(self, chroma_persist_dir: str = "./data/chroma"):
        self.chroma_persist_dir = chroma_persist_dir
        self.index = None
        self.embed_model = None
        self._initialize_components()
    
    def _initialize_components(self):
        try:
            os.makedirs(self.chroma_persist_dir, exist_ok=True)
            
            chroma_client = chromadb.PersistentClient(path=self.chroma_persist_dir)
            chroma_collection = chroma_client.get_or_create_collection("chat_history")
            
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                logger.warning("DASHSCOPE_API_KEY not found, using local ModelScope model")
                # 使用ModelScope本地模型 - 超轻量级中文嵌入模型，适合2G内存环境
                self.embed_model = ModelScopeEmbedding(
                    model_name="BAAI/bge-small-zh-v1.5"
                )
            else:
                # 使用DashScope远程模型
                from langchain_community.embeddings import DashScopeEmbeddings
                from llama_index.embeddings.langchain import LangchainEmbedding
                langchain_embedding = DashScopeEmbeddings(
                    model="text-embedding-v1"
                )
                self.embed_model = LangchainEmbedding(langchain_embedding)
            
            self.node_parser = SentenceSplitter(
                separator=" ",
                chunk_size=512,
                chunk_overlap=128
            )
            
            # Set global embedding model to avoid conflicts
            Settings.embed_model = self.embed_model
            
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    storage_context=storage_context,
                    embed_model=self.embed_model
                )
                logger.info("Loaded existing vector index")
            except Exception as e:
                logger.info(f"Creating new vector index: {e}")
                self.index = VectorStoreIndex(
                    [],
                    storage_context=storage_context,
                    embed_model=self.embed_model
                )
              
            logger.info("LlamaIndex service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex service: {e}")
            raise
    
    def _extract_chat_history(self) -> List[Document]:
        documents = []
        try:
            sessions = get_chat_sessions()
            for session in sessions:
                session_id = session["id"]
                session_name = session["session_name"]
                
                messages = get_chat_messages(session_id)
                for msg in messages:
                    content = msg["content"]
                    role = msg["role"]
                    
                    doc_text = f"[{session_name}] {role}: {content}"
                    metadata = {
                        "session_id": session_id,
                        "session_name": session_name,
                        "role": role,
                        "message_id": msg["id"],
                        "created_at": msg["created_at"]
                    }
                    
                    documents.append(Document(text=doc_text, metadata=metadata))
            
            logger.info(f"Extracted {len(documents)} documents from chat history")
            return documents
        except Exception as e:
            logger.error(f"Failed to extract chat history: {e}")
            return []
    
    def build_index(self, force_rebuild: bool = False):
        try:
            if force_rebuild or self.index is None:
                documents = self._extract_chat_history()
                
                if not documents:
                    logger.warning("No documents found to build index")
                    return
                
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
            else:
                logger.info("Index already exists, skipping rebuild")
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            raise
    
    def update_index(self, session_id: int):
        try:
            session = get_chat_sessions()
            target_session = next((s for s in session if s["id"] == session_id), None)
            
            if not target_session:
                logger.warning(f"Session {session_id} not found")
                return
            
            messages = get_chat_messages(session_id)
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
                    "created_at": msg["created_at"]
                }
                
                documents.append(Document(text=doc_text, metadata=metadata))
            
            if documents:
                for doc in documents:
                    self.index.insert(doc)
                
                logger.info(f"Updated index with {len(documents)} documents from session {session_id}")
        except Exception as e:
            logger.error(f"Failed to update index for session {session_id}: {e}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        try:
            # Always build index before search to ensure data is available
            logger.info("Building index before search...")
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

_llamaindex_service: Optional[LlamaIndexService] = None

def get_llamaindex_service() -> LlamaIndexService:
    global _llamaindex_service
    if _llamaindex_service is None:
        _llamaindex_service = LlamaIndexService()
    return _llamaindex_service

# 创建全局LlamaIndex服务实例
llamaindex_service = get_llamaindex_service()