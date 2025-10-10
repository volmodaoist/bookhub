from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut, BatchUsersOut
from app.storage.user.user_interface import IUserRepository

from contextlib import contextmanager
from typing import Optional, List, Dict, Union

import logging


""" 此处涉及的几个要素:
 
    - 数据事务

    
    - 几种异常抛出方式
        1. raise
            直接抛出当前异常，保留原始异常栈信息
        2. raise e       
            直接抛出当前异常，但是在之前的信息会丢失
        3. raise Exception("message") from e  
            附带额外的报错信息 "message"，同时保留原始异常作为上下文, 形成一大串异常链
        4. raise ValueError("message") 
            只抛出当前异常栈信息 (在此之前的调用栈信息不被抛出), 终端给出报错信息会相对少一点
            
    数据访问层只抛异常，不对异常进行过多的处理，异常的处理交给上层来解决(通常是接口层, 或者业务逻辑层, 取决于设计者)
"""


# 使用 Python上下文管理器来处理数据库事务, 在失败的时候自动回滚, 通过事务管理器来保证原子性
# 成功时提交事务(commit),  commit 完成之后才能调用 refresh 获取最新状态;  失败时回滚事务, 打印异常调用栈，并且重新向上抛出异常!
@contextmanager
def transaction(db: Session):
    try:
        yield db
        db.commit()
    except Exception as e:
        logging.exception(e)
        db.rollback()
        raise
    
    

# 这是 PySQL+SQLAlchemy 实现的用户仓库(业务逻辑传入的参数是一个 IUserRepository 类型，而不是具体的子类)
# 因而可以很方便地替换为其他子类实现，比如基于 PGSQL、MongoDB 用户仓库，或是换成 MySQL 其它三方库, e.g. SQLModel 实现
class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_uid(self, uid: int) -> Optional[UserOut]:
        user = self.db.query(User).filter(User.uid == uid).first()
        return UserOut.model_validate(user) if user else None

    def get_user_by_student_id(self, student_id: str) -> Optional[UserOut]:
        user = self.db.query(User).filter(User.student_id == student_id).first()
        return UserOut.model_validate(user) if user else None

    def get_batch_users(self, page: int, page_size: int) -> Optional[BatchUsersOut]:
        # 获取用户列表
        users = (
            self.db.query(User)
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )
        # 获取总记录数
        total = self.db.query(User).count()

        # 返回分页后的用户信息 (由的BatchUsersOut 是一个嵌套的 Pydantic BaseModel, 故需要手动调用一下 model_dump 方法来做序列的)
        return BatchUsersOut(total=total, count=len(users), users=[UserOut.model_validate(u) for u in users]).model_dump()


    def create_user(self, user_data: UserCreate) -> UserOut:
        user = User(**user_data.dict())
        
        # 使用事务管理器来将添加新用户到数据库
        
        with transaction(self.db):
            self.db.add(user)
        
        # 获取并更新用户的最新状态（比如自增的 uid）
        self.db.refresh(user)  
        return UserOut.model_validate(user).model_dump()


    def create_batch_users(self, users: List[UserCreate]) -> List[UserOut]:
        user_orms = [User(**u.dict()) for u in users]
        
        # 使用事务管理器批量添加用户
        with transaction(self.db):
            self.db.add_all(user_orms)
        
        # 调用 refresh 处理的实体，必须是已经在库内的实体(因而创建操作需要先做commit 才能刷新)
        for user in user_orms:
            self.db.refresh(user)  

        return [UserOut.model_validate(user) for user in user_orms]


    def update_user(self, student_id: str, user_data: UserUpdate) -> Optional[UserOut]:
        user = self.db.query(User).filter(User.student_id == student_id).first()
        
        if not user:
            return None
                
        # 使用事务管理器, 刷新用户信息，确保数据库中的数据更新到最新
        with transaction(self.db):
            # 更新用户属性
            for field, value in user_data.dict(exclude_unset=True).items():
                setattr(user, field, value)
        
        self.db.refresh(user)
        return UserOut.model_validate(user).model_dump()


    def delete_user(self, student_id: str) -> Optional[UserOut]:
        user = self.db.query(User).filter(User.student_id == student_id).first()
        
        if not user:
            raise ValueError(f"User with student_id {student_id} not found.")
        
        # 使用事务管理器
        with transaction(self.db):
            user_info = UserOut.model_validate(user).model_dump()
            self.db.delete(user)  # 删除用户

        return user_info