from fastapi import APIRouter, Body, Depends, Query, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.services.db import get_db_connection
from app.api.auth import get_current_user, USER_ACCOUNTS
import json
import sqlite3
from datetime import datetime
from app.exceptions import BusinessException, ValidationException, ErrorCode

router = APIRouter(prefix="/assistant", tags=["assistant"])

# Pydantic模型
class GoalCreate(BaseModel):
    title: str
    description: str

class GoalResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    created_by: str
    created_at: str

class GoalListResponse(BaseModel):
    id: int
    title: str
    status: str
    created_by: str
    created_at: str

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    assignee: str
    assignee_role: str
    parent_id: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    assignee: str
    assignee_role: str
    parent_id: Optional[int]
    created_by: str
    created_at: str

class TaskStatusUpdate(BaseModel):
    status: str

class DecomposeResponse(BaseModel):
    success: bool
    message: str
    task_count: int

class UserResponse(BaseModel):
    username: str
    role: str

@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    goal: GoalCreate,
    request: Request
):
    """
    创建新目标
    """
    # 从request.state中获取visitor_id
    visitor_id = getattr(request.state, 'visitor_id', None)
    
    # 从USER_ACCOUNTS中查找用户
    current_user = None
    for account in USER_ACCOUNTS:
        if account["username"] == visitor_id:
            current_user = account
            break
    
    if not current_user:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message="无效的用户"
        )
    
    # 只有总裁可以创建目标
    if current_user.get("role") != "总裁":
        raise BusinessException(
            code=ErrorCode.PERMISSION_DENIED,
            message="只有总裁可以创建目标"
        )
    
    # 任务数据库是公共的，需要多人协助，只有一份，不同于个人聊天私人数据
    conn = get_db_connection("default")
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO goals (title, description, status, created_by) VALUES (?, ?, ?, ?)",
            (goal.title, goal.description, "待分解", current_user.get("sub"))
        )
        goal_id = cursor.lastrowid
        conn.commit()
        
        # 获取创建的目标
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        goal_data = cursor.fetchone()
        
        return GoalResponse(
            id=goal_data[0],
            title=goal_data[1],
            description=goal_data[2],
            status=goal_data[3],
            created_by=goal_data[4],
            created_at=goal_data[5]
        )
    finally:
        conn.close()

@router.get("/goals", response_model=List[GoalListResponse])
async def get_goals(
    request: Request
):
    """
    获取目标列表
    """
    # 从request.state中获取visitor_id
    visitor_id = getattr(request.state, 'visitor_id', None)
    
    # 从USER_ACCOUNTS中查找用户
    current_user = None
    for account in USER_ACCOUNTS:
        if account["username"] == visitor_id:
            current_user = account
            break
    
    if not current_user:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message="无效的用户"
        )
    
    # 任务数据库是公共的，需要多人协助，只有一份，不同于个人聊天私人数据
    conn = get_db_connection("default")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, title, status, created_by, created_at FROM goals ORDER BY created_at DESC")
        goals = cursor.fetchall()
        
        return [
            GoalListResponse(
                id=goal[0],
                title=goal[1],
                status=goal[2],
                created_by=goal[3],
                created_at=goal[4]
            )
            for goal in goals
        ]
    finally:
        conn.close()

@router.post("/goals/{goal_id}/decompose", response_model=DecomposeResponse)
async def decompose_goal(
    goal_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    分解目标为子任务
    """
    # 只有总裁可以分解目标
    if current_user.get("role") != "总裁":
        raise BusinessException(
            code=ErrorCode.PERMISSION_DENIED,
            message="只有总裁可以分解目标"
        )
    
    conn = get_db_connection('default')
    cursor = conn.cursor()
    
    try:
        # 检查目标是否存在
        cursor.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        goal = cursor.fetchone()
        if not goal:
            raise BusinessException(
                code=ErrorCode.RESOURCE_NOT_FOUND,
                message="目标不存在"
            )
        
        # 更新目标状态为分解中
        cursor.execute("UPDATE goals SET status = '分解中', updated_at = ? WHERE id = ?", 
                      (datetime.now().isoformat(), goal_id))
        
        # 模拟大模型分解结果（实际项目中应调用真实的大模型API）
        mock_tasks = [
            {
                "title": "市场调研",
                "description": "对目标市场进行详细调研，分析竞争情况",
                "role": "市场",
                "priority": "高"
            },
            {
                "title": "产品规划",
                "description": "基于市场调研结果，制定产品规划方案",
                "role": "运营",
                "priority": "高"
            },
            {
                "title": "技术架构设计",
                "description": "设计产品的技术架构和技术选型",
                "role": "研发",
                "priority": "高"
            },
            {
                "title": "预算规划",
                "description": "制定项目预算和成本控制方案",
                "role": "财务",
                "priority": "中"
            },
            {
                "title": "项目管理",
                "description": "协调各部门工作，确保项目按时完成",
                "role": "总裁",
                "priority": "高"
            }
        ]
        
        # 创建任务
        task_count = 0
        for task_data in mock_tasks:
            # 找到对应角色的用户
            assignee = None
            for user in USER_ACCOUNTS:
                if user["role"] == task_data["role"]:
                    assignee = user["username"]
                    break
            
            if assignee:
                cursor.execute(
                    "INSERT INTO tasks (title, description, status, priority, assignee, assignee_role, parent_id, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (task_data["title"], task_data["description"], "待处理", task_data["priority"], 
                     assignee, task_data["role"], None, current_user.get("sub"))
                )
                task_count += 1
        
        # 更新目标状态为已分解
        cursor.execute("UPDATE goals SET status = '已分解', updated_at = ? WHERE id = ?", 
                      (datetime.now().isoformat(), goal_id))
        
        conn.commit()
        
        return DecomposeResponse(
            success=True,
            message="目标分解成功",
            task_count=task_count
        )
    finally:
        conn.close()

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    request: Request,
    assignee: Optional[str] = Query(None, description="按负责人筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    parent_id: Optional[int] = Query(None, description="按父任务ID筛选")
):
    """
    获取任务列表
    """
    # 从request.state中获取visitor_id
    visitor_id = getattr(request.state, 'visitor_id', None)
    
    # 从USER_ACCOUNTS中查找用户
    current_user = None
    for account in USER_ACCOUNTS:
        if account["username"] == visitor_id:
            current_user = account
            break
    
    if not current_user:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message="无效的用户"
        )
    
    # 任务数据库是公共的，需要多人协助，只有一份，不同于个人聊天私人数据
    conn = get_db_connection("default")
    cursor = conn.cursor()
    
    try:
        # 构建查询
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        # 普通用户只能查看自己的任务
        if current_user.get("role") != "总裁":
            query += " AND assignee = ?"
            params.append(current_user.get("sub"))
        elif assignee:
            query += " AND assignee = ?"
            params.append(assignee)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if parent_id is not None:
            query += " AND parent_id = ?"
            params.append(parent_id)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        
        return [
            TaskResponse(
                id=task[0],
                title=task[1],
                description=task[2],
                status=task[3],
                priority=task[4],
                assignee=task[5],
                assignee_role=task[6],
                parent_id=task[7],
                created_by=task[8],
                created_at=task[9]
            )
            for task in tasks
        ]
    finally:
        conn.close()

@router.put("/tasks/{task_id}/status", response_model=Dict[str, Any])
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    request: Request
):
    """
    更新任务状态
    """
    # 从request.state中获取visitor_id
    visitor_id = getattr(request.state, 'visitor_id', None)
    
    # 从USER_ACCOUNTS中查找用户
    current_user = None
    for account in USER_ACCOUNTS:
        if account["username"] == visitor_id:
            current_user = account
            break
    
    if not current_user:
        raise BusinessException(
            code=ErrorCode.AUTHENTICATION_FAILED,
            message="无效的用户"
        )
    
    # 任务数据库是公共的，需要多人协助，只有一份，不同于个人聊天私人数据
    conn = get_db_connection("default")
    cursor = conn.cursor()
    
    try:
        # 检查任务是否存在
        cursor.execute("SELECT assignee FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()
        if not task:
            raise BusinessException(
                code=ErrorCode.RESOURCE_NOT_FOUND,
                message="任务不存在"
            )
        
        # 只有任务负责人或总裁可以更新状态
        if task[0] != current_user.get("sub") and current_user.get("role") != "总裁":
            raise BusinessException(
                code=ErrorCode.PERMISSION_DENIED,
                message="只有任务负责人或总裁可以更新任务状态"
            )
        
        # 更新状态
        cursor.execute(
            "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
            (status_update.status, datetime.now().isoformat(), task_id)
        )
        
        if cursor.rowcount == 0:
            raise BusinessException(
                code=ErrorCode.RESOURCE_NOT_FOUND,
                message="任务不存在"
            )
        
        conn.commit()
        
        return {
            "id": task_id,
            "status": status_update.status,
            "updated_at": datetime.now().isoformat()
        }
    finally:
        conn.close()

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    获取用户列表（包含角色信息）
    """
    return [
        UserResponse(username=user["username"], role=user["role"])
        for user in USER_ACCOUNTS
    ]