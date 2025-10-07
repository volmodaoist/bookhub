from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate,  UserUpdate
from app.core.biz_reposone import BizResponse
from app.service import user_svc
from app.storage.db_sqlalchemy import get_db, Session

from typing import List


router = APIRouter()


@router.get("/users")
def query_batch_users(page: int = 0, page_size: int = 10, db: Session = Depends(get_db)):
    try:
        result = user_svc.get_batch_users(db, page, page_size)
        return BizResponse(data=result)
    except Exception as e:
        return BizResponse(data=list(), msg=str(e), status_code=500)
    
    
@router.get("/user/{uid}")
def query_user(uid: int, db: Session = Depends(get_db)):
    try:
        user = user_svc.get_user_by_uid(db, uid)
        return BizResponse(data=user)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)


@router.post("/users")
def create_batch_users(users: List[UserCreate], db: Session = Depends(get_db)):
    try:
        new_user = user_svc.create_batch_users(db, users)
        return BizResponse(data=new_user)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)
    


@router.post("/user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = user_svc.create_user(db, user)
        return BizResponse(data=new_user)
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)



@router.delete("/users/{uid}")
def delete_user(uid: int, db: Session = Depends(get_db)):
    try:
        user_svc.delete_user(db, uid)
        return BizResponse(data=True)
    except Exception as e:
        return BizResponse(data=False, msg=str(e), status_code=500)



@router.put("/users/{uid}")
def update_user(uid: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    try:
        user = user_svc.update_user(db, uid, user_update)
        if user:
            return BizResponse(data=user)
        else:
            return BizResponse(data=user, msg=f"updated failed: {uid} not found.")
    
    except Exception as e:
        return BizResponse(data=None, msg=str(e), status_code=500)