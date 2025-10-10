from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate,  UserUpdate
from app.core.biz_reposone import BizResponse
from app.service import user_svc
from app.storage.db import get_db, get_user_repo, Session
from app.storage.user.SQLAlchemyUserRepository import SQLAlchemyUserRepository
from app.storage.user.user_interface import IUserRepository

from typing import List


# 只有查询在接口层暴露批量查询，其余 增/删/改 操作, 只在业务层提供，不对外暴露批量处理的接口
router = APIRouter()


@router.get("/users")
def query_batch_users(page: int = 0, page_size: int = 10, repo: IUserRepository = Depends(get_user_repo)):
    try:
        result = user_svc.get_batch_users(repo, page, page_size)
        return BizResponse(data=result)
    except Exception as e:
        return BizResponse(data=list(), msg=str(e), status_code=500)
    
    
@router.get("/users/{student_id}")
def query_user(student_id: int, repo: IUserRepository = Depends(get_user_repo)):
    try:
        user = user_svc.get_user_by_student_id(repo, student_id)
        return BizResponse(data=user)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)


    
@router.post("/users")
def create_user(user: UserCreate, repo: IUserRepository = Depends(get_user_repo)):
    try:
        user_info = user_svc.create_user(repo, user)
        return BizResponse(data=user_info)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)



@router.delete("/users/{student_id}")
def delete_user(student_id: int, repo: IUserRepository = Depends(get_user_repo)):
    try:
        user_info = user_svc.delete_user(repo, student_id)
        return BizResponse(data=user_info)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)



@router.put("/users/{student_id}")
def update_user(student_id: int, user_update: UserUpdate, repo: IUserRepository = Depends(get_user_repo)):
    try:
        user_info = user_svc.update_user(repo, student_id, user_update)
        if user_info:
            return BizResponse(data=user_info)
        else:
            return BizResponse(data=user_info, msg=f"updated failed: {student_id} not found.")
    
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)