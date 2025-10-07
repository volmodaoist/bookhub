from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import (
    UserCreate, 
    UserUpdate,
    UserOut,
    BatchUsersOut
)

from typing import Optional, Dict, List



# 批量查询学生（可分页）
def get_batch_users(db: Session, page: int = 0, page_size: int = 10) -> Dict:
    skip = page * page_size
    users = db.query(User).offset(skip).limit(page_size).all()
    total = db.query(User).count()
    
    return BatchUsersOut(total=total, count=len(users), users=users).model_dump()


# 基于技术逐主键 uid 获取学生
def get_user_by_uid(db: Session, uid: int) -> Optional[Dict]:
    user = db.query(User).filter(User.uid == uid).first()
    if not user:
        return None

    return UserOut.model_validate(user).model_dump()

# 根据业务主键学号获取学生
def get_user_by_student_id(db: Session, student_id: str) -> Optional[User]:
    user = db.query(User).filter(User.student_id == student_id).first()
    if not user:
        return None
    return UserOut.model_validate(user).model_dump()



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
def update_user(db: Session, uid: int, user_data: UserUpdate) -> User:
    user = get_user_by_uid(db, uid)
    if not user:
        return None
    
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user




# 删除学生
def delete_user(db: Session, uid: int):
    user = get_user_by_uid(db, uid)
    if not user:
        raise ValueError(f"User with uid {uid} not found.")
    
    db.delete(user)
    db.commit()
