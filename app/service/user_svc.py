from app.models.user import User
from app.schemas.user import (
    UserCreate, 
    UserUpdate,
    UserOut,
    BatchUsersOut
)

from typing import Optional, Dict, List
from app.storage.user.user_interface import IUserRepository
from sqlalchemy.orm import Session



# 批量查询学生（可分页）
def get_batch_users(repo: IUserRepository, page: int = 0, page_size: int = 10) -> Dict:    
    return repo.get_batch_users(page=page, page_size=page_size)


# 基于技术逐主键 uid 获取学生
def get_user_by_uid(repo: IUserRepository, uid: int, to_dict: bool = True) -> Optional[Dict]:
    user = repo.get_user_by_uid(uid)
    if not user:
        return None
    return user.model_dump() if to_dict and user else user

# 根据业务主键学号获取学生
def get_user_by_student_id(repo: IUserRepository,  student_id: str, to_dict: bool = True) -> Optional[Dict]:
    user = repo.get_user_by_student_id(student_id)
    if not user:
        return None
    return user.model_dump() if to_dict else user

# TODO 以下代码尚未完成更新，仍一部分 db


# 批量创建学生
def create_batch_users(db: Session, users: List[UserCreate]) -> Dict:
    user_orms = [User(**u.dict()) for u in users]
    
    db.add_all(user_orms)
    db.commit()
    
    # 逐个 refresh，以便获取自增主键 uid 等
    for user in user_orms:
        db.refresh(user)
        
    return BatchUsersOut(total=len(users), count=len(users), users=user_orms).model_dump()



# 批量创建学生
def create_user(db: Session, user_data: UserCreate) -> Dict:
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserCreate.model_validate(user).model_dump()

   

# 更新学生信息
def update_user(db: Session, student_id: int, user_data: UserUpdate) -> Optional[Dict]:
    user = get_user_by_student_id(db, student_id, to_dict=False)
    if not user:
        return None
    
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserOut.model_validate(user).model_dump()




# 删除学生
def delete_user(db: Session, student_id: int):
    user = get_user_by_student_id(db, student_id, to_dict=False)
    if not user:
        raise ValueError(f"User with uid {student_id} not found.")
    
    db.delete(user)
    db.commit()
