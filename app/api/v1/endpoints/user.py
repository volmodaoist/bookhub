from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate,  UserUpdate
from app.core.biz_reposone import BizResponse
from app.service import user_svc
from app.storage.db import get_db, get_user_repo, Session
from app.storage.user.SQLAlchemyUserRepository import SQLAlchemyUserRepository
from app.storage.user.user_interface import IUserRepository

from typing import List


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


# TODO 以下代码尚未完成替换，仍有一部分 db, 需要改成 repo (设计模式里面的仓库模式)

@router.post("/users")
def create_batch_users(users: List[UserCreate], repo: IUserRepository = Depends(get_user_repo)):
    try:
        new_user = user_svc.create_batch_users(repo, users)
        return BizResponse(data=new_user)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)
    


@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = user_svc.create_user(db, user)
        return BizResponse(data=new_user)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)



@router.delete("/users/{student_id}")
def delete_user(student_id: int, db: Session = Depends(get_db)):
    try:
        user_svc.delete_user(db, student_id)
        return BizResponse(data=True)
    except Exception as e:
        return BizResponse(data=False, msg=str(e), status_code=500)



@router.put("/users/{student_id}")
def update_user(student_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = user_svc.update_user(db, student_id, user_update)
        if user:
            return BizResponse(data=user)
        else:
            return BizResponse(data=user, msg=f"updated failed: {student_id} not found.")
    
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)