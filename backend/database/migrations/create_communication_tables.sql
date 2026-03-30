-- 创建沟通消息表
CREATE TABLE IF NOT EXISTS communication_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id TEXT NOT NULL,
    receiver_id TEXT NOT NULL,
    original_content TEXT NOT NULL,
    polished_content TEXT NOT NULL,
    sender_role TEXT NOT NULL,
    receiver_role TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建回复建议表
CREATE TABLE IF NOT EXISTS response_suggestion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    suggestion_type TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES communication_message (id)
);

-- 创建用户角色表
CREATE TABLE IF NOT EXISTS user_role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 初始化用户角色数据
INSERT OR IGNORE INTO user_role (role_name, description) VALUES
('总裁', '公司最高领导者，负责公司战略决策和整体管理'),
('市场', '负责公司市场推广、品牌建设和客户关系管理'),
('运营', '负责公司日常运营管理和流程优化'),
('研发', '负责公司产品研发、技术创新和系统维护'),
('财务', '负责公司财务管理、预算控制和财务报表'),
('用户', '系统普通用户，使用各种功能和服务');

-- 创建沟通消息索引
CREATE INDEX IF NOT EXISTS idx_communication_message_sender_id ON communication_message(sender_id);
CREATE INDEX IF NOT EXISTS idx_communication_message_receiver_id ON communication_message(receiver_id);
CREATE INDEX IF NOT EXISTS idx_communication_message_created_at ON communication_message(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_communication_message_status ON communication_message(status);

-- 创建回复建议索引
CREATE INDEX IF NOT EXISTS idx_response_suggestion_message_id ON response_suggestion(message_id);
CREATE INDEX IF NOT EXISTS idx_response_suggestion_type ON response_suggestion(suggestion_type);

-- 创建用户角色索引
CREATE INDEX IF NOT EXISTS idx_user_role_role_name ON user_role(role_name);