#!/usr/bin/env python3
"""
数据库迁移脚本
执行SQL语句创建协助助手功能所需的表结构
"""
import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'xueyang.db')

# SQL文件路径
SQL_FILE = os.path.join(os.path.dirname(__file__), 'migrations', 'create_goal_task_tables.sql')

def run_migration():
    """
    执行数据库迁移
    """
    try:
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 读取SQL文件
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行SQL脚本
        cursor.executescript(sql_script)
        
        # 提交事务
        conn.commit()
        
        print("数据库迁移成功！")
        print("已创建：")
        print("1. goals表 - 存储目标信息")
        print("2. tasks表 - 存储任务信息")
        
    except Exception as e:
        print(f"数据库迁移失败: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration()