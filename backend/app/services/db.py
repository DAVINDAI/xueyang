import sqlite3
import os
from typing import List, Dict, Any
from contextlib import contextmanager
import logging

# 数据库基础路径
db_base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# 配置日志
logger = logging.getLogger(__name__)

@contextmanager
def db_connection(visitor_id):
    """数据库连接上下文管理器，确保连接正确关闭"""
    conn = get_db_connection(visitor_id)
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
def init_database(visitor_id=None):
    """初始化数据库，创建必要的表结构"""
    # 如果没有visitor_id，使用默认数据库路径
    if not visitor_id:
        logger.info("未提供visitor_id，使用默认数据库路径")
        db_path = os.path.join(db_base_path, 'langgraph_data.db')
    else:
        # 构建数据库路径
        db_path = os.path.join(db_base_path, visitor_id, 'langgraph_data.db')
    
    logger.info(f"初始化数据库: {db_path}")
    
    # 确保数据库目录存在
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"创建数据库目录: {db_dir}")
    
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
    
    # 创建笔记表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        user_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建编程题目表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS problems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        difficulty INTEGER NOT NULL,  -- 1: 简单, 2: 中等, 3: 困难
        examples TEXT NOT NULL,  -- JSON格式存储示例输入输出
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建用户答案表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        problem_id INTEGER NOT NULL,
        user_code TEXT NOT NULL,
        evaluation_result TEXT NOT NULL,  -- JSON格式存储评估结果
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (problem_id) REFERENCES problems (id)
    )
    ''')
    
    # 创建索引 - 提升查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_message_session_id ON chat_message(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_message_created_at ON chat_message(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memo_message_original_session_id ON memo_message(original_session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memo_message_created_at ON memo_message(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resume_optimization_created_at ON resume_optimization(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notes_updated_at ON notes(updated_at DESC)')
    
    # 提交事务
    conn.commit()
    conn.close()

# 获取数据库连接
def get_db_connection(visitor_id):
    """获取数据库连接，使用澳门时区（Asia/Macau）"""
    # 设置时区为澳门时区（东8区）
    os.environ['TZ'] = 'Asia/Macau'
    import time
    try:
        time.tzset()
    except AttributeError:
        pass  # Windows不支持tzset
    
    # 打印数据库路径
    # visitor_id 为空或为 "default" 时，使用默认数据库路径
    if not visitor_id or visitor_id == "default":
        logger.info(f"visitor_id为空或为default，使用默认数据库路径")
        db_path = os.path.join(db_base_path, 'langgraph_data.db')
    else:
        logger.info(f"使用visitor_id: {visitor_id}，数据库路径")
        db_path = os.path.join(db_base_path, visitor_id, 'langgraph_data.db')
    
    logger.info(f"数据库路径: {db_path}")
    
    # 确保数据库目录存在并初始化
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        # 初始化数据库表结构
        init_database(visitor_id)
    
    logger.info(f"数据库连接: {db_path}，visitor_id: {visitor_id}")
    # 原来problems是单独的数据库，现在合并到langgraph_data数据库中，需要重新初始化
    if visitor_id == "17800212735":
        logger.info(f"合并数据库: {db_path}")
        # 初始化数据库表结构
        init_database(visitor_id)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    return conn

# 聊天会话操作
def create_chat_session(visitor_id: str, session_name: str, model_name: str) -> int:
    """创建聊天会话"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO chat_session (session_name, model_name) VALUES (?, ?)
    ''', (session_name, model_name))
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def get_chat_sessions(visitor_id: str) -> List[Dict[str, Any]]:
    """获取所有聊天会话"""
    conn = get_db_connection(visitor_id)
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

def get_chat_session(visitor_id: str, session_id: int) -> Dict[str, Any]:
    """获取单个聊天会话"""
    conn = get_db_connection(visitor_id)
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

def update_chat_session(visitor_id: str, session_id: int, session_name: str) -> bool:
    """更新聊天会话"""
    conn = get_db_connection(visitor_id)
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

def delete_chat_session(visitor_id: str, session_id: int) -> bool:
    """删除聊天会话"""
    conn = get_db_connection(visitor_id)
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
def save_chat_message(visitor_id: str, session_id: int, role: str, content: str, token_count: int = None) -> int:
    """保存聊天消息"""
    conn = get_db_connection(visitor_id)
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

def get_chat_messages(visitor_id: str, session_id: int) -> List[Dict[str, Any]]:
    """获取聊天消息"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, session_id, role, content, created_at, token_count 
    FROM chat_message 
    WHERE session_id = ? 
    ORDER BY created_at ASC
    ''', (session_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    # 转换时间格式
    for message in messages:
        message['created_at'] = convert_db_time_to_iso(message['created_at'])
    conn.close()
    return messages

def delete_chat_message(visitor_id: str, message_id: int) -> bool:
    """删除聊天消息"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_message WHERE id = ?', (message_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# 统计信息操作
def get_stats(visitor_id: str) -> Dict[str, Any]:
    """获取统计信息"""
    conn = get_db_connection(visitor_id)
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
def get_session_details(visitor_id: str, session_id: int = None) -> Dict[str, Any]:
    """获取会话详情"""
    conn = get_db_connection(visitor_id)
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
        
        messages = get_chat_messages(visitor_id, session_id)
        
        conn.close()
        
        return {
            "session": session,
            "messages": messages
        }
    else:
        # 获取所有会话的简要信息
        sessions = get_chat_sessions(visitor_id)
        
        # 为每个会话添加消息数量
        for session in sessions:
            cursor.execute('SELECT COUNT(*) FROM chat_message WHERE session_id = ?', (session['id'],))
            session['message_count'] = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "sessions": sessions
        }

# 备忘录操作
def create_memo_message(visitor_id: str, original_session_id: int, original_message_id: int, content: str) -> int:
    """创建备忘录消息"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO memo_message (original_session_id, original_message_id, content) 
    VALUES (?, ?, ?)
    ''', (original_session_id, original_message_id, content))
    memo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memo_id

def get_memo_messages(visitor_id: str) -> List[Dict[str, Any]]:
    """获取所有备忘录消息"""
    conn = get_db_connection(visitor_id)
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

def get_memo_message(visitor_id: str, memo_id: int) -> Dict[str, Any]:
    """获取单个备忘录消息"""
    conn = get_db_connection(visitor_id)
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

def get_memo_messages_by_session(visitor_id: str, original_session_id: int) -> List[Dict[str, Any]]:
    """获取指定会话的所有备忘录消息"""
    conn = get_db_connection(visitor_id)
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

def delete_memo_message(visitor_id: str, memo_id: int) -> bool:
    """删除备忘录消息"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM memo_message WHERE id = ?', (memo_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def add_indexes_to_existing_db(visitor_id=None):
    """为现有数据库添加索引（用于迁移）"""
    # 如果没有visitor_id，使用默认数据库路径
    if not visitor_id:
        logger.info("未提供visitor_id，使用默认数据库路径添加索引")
        db_path = os.path.join(db_base_path, 'langgraph_data.db')
    else:
        db_path = os.path.join(db_base_path, visitor_id, 'langgraph_data.db')
    
    logger.info(f"为数据库添加索引: {db_path}")
    
    # 确保数据库目录存在
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        logger.warning(f"数据库目录不存在: {db_dir}，跳过索引添加")
        return
    
    conn = sqlite3.connect(db_path)
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

def search_chat_messages(visitor_id: str, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """搜索聊天消息内容"""
    conn = get_db_connection(visitor_id)
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
def save_resume_optimization(visitor_id: str, job_title: str, job_description: str, industry_analysis: str, 
                            optimized_resume: str, optimization_suggestions: list, 
                            matching_analysis: dict, interview_preparation: str) -> int:
    """保存简历优化结果"""
    import json
    conn = get_db_connection(visitor_id)
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

def get_resume_optimizations(visitor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """获取所有简历优化结果"""
    import json
    conn = get_db_connection(visitor_id)
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

def get_resume_optimization(visitor_id: str, optimization_id: int) -> Dict[str, Any]:
    """获取单个简历优化结果"""
    import json
    conn = get_db_connection(visitor_id)
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

def delete_resume_optimization(visitor_id: str, optimization_id: int) -> bool:
    """删除简历优化结果"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM resume_optimization WHERE id = ?', (optimization_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# 笔记操作
def create_note(visitor_id: str, title: str, content: str, user_id: int = None) -> int:
    """创建笔记"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO notes (title, content, user_id) 
    VALUES (?, ?, ?)
    ''', (title, content, user_id))
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return note_id

def get_notes(visitor_id: str, user_id: int = None) -> List[Dict[str, Any]]:
    """获取笔记列表"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute('''
        SELECT id, title, content, user_id, created_at, updated_at 
        FROM notes 
        WHERE user_id = ? 
        ORDER BY updated_at DESC
        ''', (user_id,))
    else:
        cursor.execute('''
        SELECT id, title, content, user_id, created_at, updated_at 
        FROM notes 
        ORDER BY updated_at DESC
        ''')
    
    notes = [dict(row) for row in cursor.fetchall()]
    # 转换时间格式
    for note in notes:
        note['created_at'] = convert_db_time_to_iso(note['created_at'])
        note['updated_at'] = convert_db_time_to_iso(note['updated_at'])
    conn.close()
    return notes

def get_note(visitor_id: str, note_id: int) -> Dict[str, Any]:
    """获取单个笔记"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, title, content, user_id, created_at, updated_at 
    FROM notes 
    WHERE id = ?
    ''', (note_id,))
    row = cursor.fetchone()
    note = dict(row) if row else None
    if note:
        note['created_at'] = convert_db_time_to_iso(note['created_at'])
        note['updated_at'] = convert_db_time_to_iso(note['updated_at'])
    conn.close()
    return note

def update_note(visitor_id: str, note_id: int, title: str, content: str) -> bool:
    """更新笔记"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE notes 
    SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP 
    WHERE id = ?
    ''', (title, content, note_id))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_note(visitor_id: str, note_id: int) -> bool:
    """删除笔记"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

# 编程题目操作
def add_problem(visitor_id: str, title: str, description: str, difficulty: int, examples: list) -> int:
    """添加编程题目"""
    import json
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    examples_json = json.dumps(examples)
    cursor.execute(
        "INSERT INTO problems (title, description, difficulty, examples) VALUES (?, ?, ?, ?)",
        (title, description, difficulty, examples_json)
    )
    
    problem_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return problem_id

def get_problem(visitor_id: str, problem_id: int) -> dict:
    """获取编程题目"""
    import json
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM problems WHERE id = ?", (problem_id,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "difficulty": row[3],
            "examples": json.loads(row[4]),
            "created_at": convert_db_time_to_iso(row[5])
        }
    return None

def get_recent_problems(visitor_id: str, limit: int = 5) -> list:
    """获取最近的编程题目"""
    import json
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM problems ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    
    conn.close()
    
    problems = []
    for row in rows:
        problems.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "difficulty": row[3],
            "examples": json.loads(row[4]),
            "created_at": convert_db_time_to_iso(row[5])
        })
    
    return problems

def get_problem_by_difficulty(visitor_id: str, difficulty: int) -> dict:
    """根据难度获取编程题目"""
    import json
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM problems WHERE difficulty = ? ORDER BY ID LIMIT 1", (difficulty,))
    row = cursor.fetchone()
    
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "difficulty": row[3],
            "examples": json.loads(row[4]),
            "created_at": convert_db_time_to_iso(row[5])
        }
    return None

def add_user_answer(visitor_id: str, problem_id: int, user_code: str, evaluation_result: dict) -> int:
    """添加用户答案"""
    import json
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    evaluation_json = json.dumps(evaluation_result)
    cursor.execute(
        "INSERT INTO user_answers (problem_id, user_code, evaluation_result) VALUES (?, ?, ?)",
        (problem_id, user_code, evaluation_json)
    )
    
    answer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return answer_id

def get_user_answers(visitor_id: str, problem_id: int, limit: int = 10) -> list:
    """获取用户答案"""
    import json
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM user_answers WHERE problem_id = ? ORDER BY created_at DESC LIMIT ?",
        (problem_id, limit)
    )
    rows = cursor.fetchall()
    
    conn.close()
    
    answers = []
    for row in rows:
        answers.append({
            "id": row[0],
            "problem_id": row[1],
            "user_code": row[2],
            "evaluation_result": json.loads(row[3]),
            "created_at": convert_db_time_to_iso(row[4])
        })
    
    return answers

def get_difficulty_stats(visitor_id: str) -> dict:
    """获取难度统计"""
    conn = get_db_connection(visitor_id)
    cursor = conn.cursor()
    
    cursor.execute("SELECT difficulty, COUNT(*) FROM problems GROUP BY difficulty")
    rows = cursor.fetchall()
    
    conn.close()
    
    stats = {1: 0, 2: 0, 3: 0}
    for row in rows:
        stats[row[0]] = row[1]
    
    return stats
