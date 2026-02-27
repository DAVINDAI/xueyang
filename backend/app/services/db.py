import sqlite3
import os
from typing import List, Dict, Any
from contextlib import contextmanager
import logging

# 数据库文件路径
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'langgraph_data.db')

# 配置日志
logger = logging.getLogger(__name__)

@contextmanager
def db_connection():
    """数据库连接上下文管理器，确保连接正确关闭"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

# 辅助函数：转换数据库时间字符串为ISO格式（带Z表示UTC）
def convert_db_time_to_iso(db_time_str):
    """将数据库时间字符串转换为标准ISO格式（带Z后缀）"""
    if not db_time_str:
        return None
    try:
        from datetime import datetime
        # 解析数据库时间字符串（当作UTC时间）
        dt = datetime.strptime(db_time_str, '%Y-%m-%d %H:%M:%S')
        # 转换为标准ISO格式，末尾加Z表示UTC时间
        return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        return db_time_str

# 初始化数据库
def init_database():
    """初始化数据库，创建必要的表结构"""
    # 确保数据库目录存在
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建聊天会话表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_session (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_name TEXT NOT NULL,
        model_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建聊天消息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        token_count INTEGER,
        FOREIGN KEY (session_id) REFERENCES chat_session (id)
    )
    ''')
    
    # 创建备忘录消息表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memo_message (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_session_id INTEGER NOT NULL,
        original_message_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (original_session_id) REFERENCES chat_session (id)
    )
    ''')
    
    # 创建简历优化结果表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resume_optimization (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT NOT NULL,
        job_description TEXT NOT NULL,
        industry_analysis TEXT,
        optimized_resume TEXT,
        optimization_suggestions TEXT,  -- JSON格式
        matching_analysis TEXT,         -- JSON格式
        interview_preparation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建索引 - 提升查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_message_session_id ON chat_message(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_message_created_at ON chat_message(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memo_message_original_session_id ON memo_message(original_session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memo_message_created_at ON memo_message(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resume_optimization_created_at ON resume_optimization(created_at DESC)')
    
    # 提交事务
    conn.commit()
    conn.close()

# 获取数据库连接
def get_db_connection():
    """获取数据库连接，使用澳门时区（Asia/Macau）"""
    # 设置时区为澳门时区（东8区）
    os.environ['TZ'] = 'Asia/Macau'
    import time
    try:
        time.tzset()
    except AttributeError:
        pass  # Windows不支持tzset
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    return conn

# 聊天会话操作
def create_chat_session(session_name: str, model_name: str) -> int:
    """创建聊天会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO chat_session (session_name, model_name) VALUES (?, ?)
    ''', (session_name, model_name))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_chat_sessions() -> List[Dict[str, Any]]:
    """获取所有聊天会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, session_name, model_name, created_at, updated_at 
    FROM chat_session 
    ORDER BY updated_at DESC
    ''')
    sessions = [dict(row) for row in cursor.fetchall()]
    # 转换时间格式
    for session in sessions:
        session['created_at'] = convert_db_time_to_iso(session['created_at'])
        session['updated_at'] = convert_db_time_to_iso(session['updated_at'])
    conn.close()
    return sessions

def get_chat_session(session_id: int) -> Dict[str, Any]:
    """获取单个聊天会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, session_name, model_name, created_at, updated_at 
    FROM chat_session 
    WHERE id = ?
    ''', (session_id,))
    row = cursor.fetchone()
    session = dict(row) if row else None
    if session:
        session['created_at'] = convert_db_time_to_iso(session['created_at'])
        session['updated_at'] = convert_db_time_to_iso(session['updated_at'])
    conn.close()
    return session

def update_chat_session(session_id: int, session_name: str) -> bool:
    """更新聊天会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE chat_session 
    SET session_name = ?, updated_at = CURRENT_TIMESTAMP 
    WHERE id = ?
    ''', (session_name, session_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_chat_session(session_id: int) -> bool:
    """删除聊天会话"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # 先删除该会话的所有消息
    cursor.execute('DELETE FROM chat_message WHERE session_id = ?', (session_id,))
    # 删除该会话的所有备忘录
    cursor.execute('DELETE FROM memo_message WHERE original_session_id = ?', (session_id,))
    # 删除会话
    cursor.execute('DELETE FROM chat_session WHERE id = ?', (session_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# 聊天消息操作
def save_chat_message(session_id: int, role: str, content: str, token_count: int = None) -> int:
    """保存聊天消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO chat_message (session_id, role, content, token_count) 
    VALUES (?, ?, ?, ?)
    ''', (session_id, role, content, token_count))
    message_id = cursor.lastrowid
    
    # 更新会话的updated_at时间
    cursor.execute('''
    UPDATE chat_session 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = ?
    ''', (session_id,))
    
    conn.commit()
    conn.close()
    return message_id

def get_chat_messages(session_id: int) -> List[Dict[str, Any]]:
    """获取聊天消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, session_id, role, content, created_at, token_count 
    FROM chat_message 
    WHERE session_id = ? 
    ORDER BY created_at ASC
    ''', (session_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    # 转换时间格式
    for msg in messages:
        msg['created_at'] = convert_db_time_to_iso(msg['created_at'])
    conn.close()
    return messages

def delete_chat_message(message_id: int) -> bool:
    """删除聊天消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_message WHERE id = ?', (message_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# 统计信息操作
def get_stats() -> Dict[str, Any]:
    """获取统计信息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 会话数量
    cursor.execute('SELECT COUNT(*) FROM chat_session')
    session_count = cursor.fetchone()[0]
    
    # 消息数量
    cursor.execute('SELECT COUNT(*) FROM chat_message')
    message_count = cursor.fetchone()[0]
    
    # 总token数
    cursor.execute('SELECT COALESCE(SUM(token_count), 0) FROM chat_message')
    total_tokens = cursor.fetchone()[0]
    
    # 备忘录数量
    cursor.execute('SELECT COUNT(*) FROM memo_message')
    memo_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'session_count': session_count,
        'message_count': message_count,
        'total_tokens': total_tokens,
        'memo_count': memo_count
    }

# 获取会话详情（包含消息）
def get_session_details(session_id: int = None) -> Dict[str, Any]:
    """获取会话详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if session_id:
        # 获取单个会话详情
        cursor.execute('''
        SELECT id, session_name, model_name, created_at, updated_at 
        FROM chat_session 
        WHERE id = ?
        ''', (session_id,))
        row = cursor.fetchone()
        session = dict(row) if row else None
        
        if session:
            session['created_at'] = convert_db_time_to_iso(session['created_at'])
            session['updated_at'] = convert_db_time_to_iso(session['updated_at'])
        
        messages = get_chat_messages(session_id)
        
        conn.close()
        
        return {
            "session": session,
            "messages": messages
        }
    else:
        # 获取所有会话的简要信息
        sessions = get_chat_sessions()
        
        # 为每个会话添加消息数量
        for session in sessions:
            cursor.execute('SELECT COUNT(*) FROM chat_message WHERE session_id = ?', (session['id'],))
            session['message_count'] = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "sessions": sessions
        }

# 备忘录操作
def create_memo_message(original_session_id: int, original_message_id: int, content: str) -> int:
    """创建备忘录消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO memo_message (original_session_id, original_message_id, content) 
    VALUES (?, ?, ?)
    ''', (original_session_id, original_message_id, content))
    memo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memo_id

def get_memo_messages() -> List[Dict[str, Any]]:
    """获取所有备忘录消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, original_session_id, original_message_id, content, created_at 
    FROM memo_message 
    ORDER BY created_at DESC
    ''')
    memos = [dict(row) for row in cursor.fetchall()]
    # 转换时间格式
    for memo in memos:
        memo['created_at'] = convert_db_time_to_iso(memo['created_at'])
    conn.close()
    return memos

def get_memo_message(memo_id: int) -> Dict[str, Any]:
    """获取单个备忘录消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, original_session_id, original_message_id, content, created_at 
    FROM memo_message 
    WHERE id = ?
    ''', (memo_id,))
    row = cursor.fetchone()
    memo = dict(row) if row else None
    if memo:
        memo['created_at'] = convert_db_time_to_iso(memo['created_at'])
    conn.close()
    return memo

def get_memo_messages_by_session(original_session_id: int) -> List[Dict[str, Any]]:
    """获取指定会话的所有备忘录消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, original_session_id, original_message_id, content, created_at 
    FROM memo_message 
    WHERE original_session_id = ? 
    ORDER BY created_at DESC
    ''', (original_session_id,))
    memos = [dict(row) for row in cursor.fetchall()]
    # 转换时间格式
    for memo in memos:
        memo['created_at'] = convert_db_time_to_iso(memo['created_at'])
    conn.close()
    return memos

def delete_memo_message(memo_id: int) -> bool:
    """删除备忘录消息"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM memo_message WHERE id = ?', (memo_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def add_indexes_to_existing_db():
    """为现有数据库添加索引（用于迁移）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_message_session_id ON chat_message(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_message_created_at ON chat_message(created_at DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memo_message_original_session_id ON memo_message(original_session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memo_message_created_at ON memo_message(created_at DESC)')
        conn.commit()
        logger.info("数据库索引添加成功")
    except Exception as e:
        logger.error(f"添加索引失败: {e}")
    finally:
        conn.close()

def search_chat_messages(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """搜索聊天消息内容"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 使用LIKE进行模糊搜索 - 虽然无法使用索引，但通过其他索引优化JOIN和排序
    cursor.execute('''
    SELECT cm.id, cm.session_id, cm.role, cm.content, cm.created_at, cs.session_name
    FROM chat_message cm
    JOIN chat_session cs ON cm.session_id = cs.id
    WHERE cm.content LIKE ?
    ORDER BY cm.created_at DESC
    LIMIT ?
    ''', (f'%{keyword}%', limit))
    
    results = [dict(row) for row in cursor.fetchall()]
    
    # 转换时间格式
    for result in results:
        result['created_at'] = convert_db_time_to_iso(result['created_at'])
    
    conn.close()
    return results

# 简历优化结果操作
def save_resume_optimization(job_title: str, job_description: str, industry_analysis: str, 
                            optimized_resume: str, optimization_suggestions: list, 
                            matching_analysis: dict, interview_preparation: str) -> int:
    """保存简历优化结果"""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 转换列表和字典为JSON字符串
    optimization_suggestions_json = json.dumps(optimization_suggestions) if optimization_suggestions else '[]'
    matching_analysis_json = json.dumps(matching_analysis) if matching_analysis else '{}'
    
    cursor.execute('''
    INSERT INTO resume_optimization (job_title, job_description, industry_analysis, 
                                   optimized_resume, optimization_suggestions, 
                                   matching_analysis, interview_preparation)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (job_title, job_description, industry_analysis, 
         optimized_resume, optimization_suggestions_json, 
         matching_analysis_json, interview_preparation))
    
    optimization_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return optimization_id

def get_resume_optimizations(limit: int = 100) -> List[Dict[str, Any]]:
    """获取所有简历优化结果"""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, job_title, job_description, industry_analysis, 
           optimized_resume, optimization_suggestions, 
           matching_analysis, interview_preparation, created_at
    FROM resume_optimization
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))
    
    optimizations = []
    for row in cursor.fetchall():
        opt = dict(row)
        # 转换时间格式
        opt['created_at'] = convert_db_time_to_iso(opt['created_at'])
        # 解析JSON字段
        if opt.get('optimization_suggestions'):
            try:
                opt['optimization_suggestions'] = json.loads(opt['optimization_suggestions'])
            except:
                opt['optimization_suggestions'] = []
        if opt.get('matching_analysis'):
            try:
                opt['matching_analysis'] = json.loads(opt['matching_analysis'])
            except:
                opt['matching_analysis'] = {}
        optimizations.append(opt)
    
    conn.close()
    return optimizations

def get_resume_optimization(optimization_id: int) -> Dict[str, Any]:
    """获取单个简历优化结果"""
    import json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, job_title, job_description, industry_analysis, 
           optimized_resume, optimization_suggestions, 
           matching_analysis, interview_preparation, created_at
    FROM resume_optimization
    WHERE id = ?
    ''', (optimization_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    opt = dict(row)
    # 转换时间格式
    opt['created_at'] = convert_db_time_to_iso(opt['created_at'])
    # 解析JSON字段
    if opt.get('optimization_suggestions'):
        try:
            opt['optimization_suggestions'] = json.loads(opt['optimization_suggestions'])
        except:
            opt['optimization_suggestions'] = []
    if opt.get('matching_analysis'):
        try:
            opt['matching_analysis'] = json.loads(opt['matching_analysis'])
        except:
            opt['matching_analysis'] = {}
    
    conn.close()
    return opt

def delete_resume_optimization(optimization_id: int) -> bool:
    """删除简历优化结果"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM resume_optimization WHERE id = ?', (optimization_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted
