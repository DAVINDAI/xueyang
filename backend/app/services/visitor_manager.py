import os
import time
import json
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# 访客数据存储文件
VISITOR_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'visitors.json')
# 最大访客数量
MAX_VISITORS = 100

class VisitorManager:
    def __init__(self):
        self.visitor_data = self._load_visitor_data()
        # 确保数据目录存在
        os.makedirs(os.path.dirname(VISITOR_DATA_FILE), exist_ok=True)
    
    def _load_visitor_data(self) -> Dict[str, Dict]:
        """加载访客数据"""
        try:
            if os.path.exists(VISITOR_DATA_FILE):
                with open(VISITOR_DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载访客数据失败: {e}")
        return {}
    
    def _save_visitor_data(self):
        """保存访客数据"""
        try:
            with open(VISITOR_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.visitor_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存访客数据失败: {e}")
    
    def update_visitor(self, visitor_id: str):
        """更新访客最后访问时间"""
        current_time = int(time.time())
        self.visitor_data[visitor_id] = {
            'last_access': current_time
        }
        
        # 检查并清理超出限制的访客
        self._cleanup_visitors()
        
        # 保存数据
        self._save_visitor_data()
    
    def _cleanup_visitors(self):
        """清理超出限制的访客，保留最近访问的MAX_VISITORS个"""
        if len(self.visitor_data) <= MAX_VISITORS:
            return
        
        # 按最后访问时间排序
        sorted_visitors = sorted(
            self.visitor_data.items(),
            key=lambda x: x[1]['last_access']
        )
        
        # 删除最久未访问的访客
        visitors_to_delete = sorted_visitors[:-MAX_VISITORS]
        for visitor_id, _ in visitors_to_delete:
            # 删除访客数据目录
            self._delete_visitor_data(visitor_id)
            # 从数据中移除
            del self.visitor_data[visitor_id]
            logger.info(f"删除访客数据: {visitor_id}")
    
    def _delete_visitor_data(self, visitor_id: str):
        """删除访客数据目录"""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', visitor_id)
        if os.path.exists(data_dir):
            try:
                import shutil
                shutil.rmtree(data_dir)
                logger.info(f"删除访客数据目录: {data_dir}")
            except Exception as e:
                logger.error(f"删除访客数据目录失败: {e}")
    
    def get_visitor_count(self) -> int:
        """获取当前访客数量"""
        return len(self.visitor_data)

# 创建全局访客管理器实例
visitor_manager = VisitorManager()