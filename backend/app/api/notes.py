from fastapi import APIRouter, HTTPException, Body, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from app.services.db import (
    create_note,
    get_notes,
    get_note,
    update_note,
    delete_note
)

router = APIRouter()

# Pydantic模型
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: str
    content: str

@router.post("/notes", response_model=Dict[str, Any])
async def create_note_endpoint(
    note: NoteCreate
):
    """
    创建笔记
    
    创建一个新的笔记。
    
    - **title**: 笔记标题
    - **content**: 笔记内容（Markdown格式）
    """
    try:
        note_id = create_note(note.title, note.content, user_id=1)  # 暂时使用固定用户ID
        return {
            "note_id": note_id,
            "title": note.title,
            "content": note.content,
            "message": "笔记创建成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建笔记失败: {str(e)}")

@router.get("/notes", response_model=List[Dict[str, Any]])
async def list_notes():
    """
    获取笔记列表
    
    返回当前用户的所有笔记。
    """
    try:
        notes = get_notes(user_id=1)  # 暂时使用固定用户ID
        return notes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取笔记列表失败: {str(e)}")

@router.get("/notes/{note_id}", response_model=Dict[str, Any])
async def get_note_endpoint(
    note_id: int
):
    """
    获取笔记详情
    
    返回指定笔记的详细信息。
    
    - **note_id**: 笔记ID
    """
    try:
        note = get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail=f"笔记不存在: {note_id}")
        return note
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取笔记详情失败: {str(e)}")

@router.put("/notes/{note_id}", response_model=Dict[str, Any])
async def update_note_endpoint(
    note_id: int,
    note: NoteUpdate
):
    """
    更新笔记
    
    更新指定笔记的内容。
    
    - **note_id**: 笔记ID
    - **title**: 新的笔记标题
    - **content**: 新的笔记内容（Markdown格式）
    """
    try:
        updated = update_note(note_id, note.title, note.content)
        if not updated:
            raise HTTPException(status_code=404, detail=f"笔记不存在: {note_id}")
        return {
            "note_id": note_id,
            "title": note.title,
            "content": note.content,
            "message": "笔记更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新笔记失败: {str(e)}")

@router.delete("/notes/{note_id}", response_model=Dict[str, Any])
async def delete_note_endpoint(
    note_id: int
):
    """
    删除笔记
    
    删除指定的笔记。
    
    - **note_id**: 笔记ID
    """
    try:
        deleted = delete_note(note_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"笔记不存在: {note_id}")
        return {
            "note_id": note_id,
            "deleted": True,
            "message": "笔记删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除笔记失败: {str(e)}")
