from app.storage.user.user_interface import IUserRepository
from app.schemas.user import (
    UserCreate, 
    UserUpdate,
    UserOut
)

from typing import Optional, Dict, List


# 批量查询学生（可分页）
def get_batch_users(repo: IUserRepository, page: int = 0, page_size: int = 10) -> List[UserOut]: 
    user_infos = repo.get_batch_users(page=page, page_size=page_size)
    return user_infos


# 基于技术逐主键 uid 获取学生
def get_user_by_uid(repo: IUserRepository, uid: int, to_dict: bool = True) -> Optional[Dict]:
    user_info = repo.get_user_by_uid(uid)
    if not user_info:
        return None
    return user_info.model_dump() if to_dict and user_info else user_info

# 根据业务主键学号获取学生
def get_user_by_student_id(repo: IUserRepository,  student_id: str, to_dict: bool = True) -> Optional[Dict]:
    user_info = repo.get_user_by_student_id(student_id)
    if not user_info:
        return None
    return user_info.model_dump() if to_dict else user_info

# 批量创建学生
def create_batch_users(repo: IUserRepository, users: List[UserCreate]) -> List[UserOut]:
    user_infos = repo.create_batch_users(users)
    return user_infos


# 批量创建学生
def create_user(repo: IUserRepository, user_data: UserCreate) -> UserOut:
    user_info = repo.create_user(user_data)
    return user_info

   
# 更新学生信息
def update_user(repo: IUserRepository, student_id: int, user_data: UserUpdate) -> Optional[UserOut]:
    user_info = repo.update_user(student_id, user_data)
    return user_info



# 删除学生
def delete_user(repo: IUserRepository,  student_id: int) -> bool:
    user_info = repo.delete_user(student_id)
    return user_info
    
    

