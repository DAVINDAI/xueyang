import logging
from typing import List
from llama_index.core.embeddings import BaseEmbedding

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
            from modelscope import AutoModel, AutoTokenizer
            logger.info(f"Loading model: {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
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
