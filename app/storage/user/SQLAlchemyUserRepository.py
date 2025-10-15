from sqlalchemy.orm import Session

from app.core.db import transaction
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut, BatchUsersOut
from app.storage.user.user_interface import IUserRepository


from typing import Optional, List


    

# 这是 PySQL+SQLAlchemy 实现的用户仓库(业务逻辑传入的参数是一个 IUserRepository 类型，而不是具体的子类)
# 因而可以很方便地替换为其他子类实现，比如基于 PGSQL、MongoDB 用户仓库，或是换成 MySQL 其它三方库, e.g. SQLModel 实现
class SQLAlchemyUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def query_student(self, student_id: str) -> User:
        return self.db.query(User).filter(User.student_id == student_id).first()

    def get_user_by_uid(self, uid: int) -> Optional[UserOut]:
        user = self.db.query(User).filter(User.uid == uid).first()
        return UserOut.model_validate(user) if user else None

    def get_user_by_student_id(self, student_id: str) -> Optional[UserOut]:
        user = self.query_student(student_id)
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
        user = self.query_student(student_id)
        
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
        user = self.query_student(student_id)
        
        if not user:
            raise ValueError(f"User with student_id {student_id} not found.")
        
        # 使用事务管理器
        with transaction(self.db):
            user_info = UserOut.model_validate(user).model_dump()
            self.db.delete(user)  # 删除用户

        return user_info