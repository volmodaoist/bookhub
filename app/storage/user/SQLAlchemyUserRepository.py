from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut, BatchUsersOut
from app.storage.user.user_interface import IUserRepository
from typing import Optional, List, Dict, Union



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

    def get_batch_users(self, page: int, page_size: int) -> List[UserOut]:
        users = (
            self.db.query(User)
            .offset(page * page_size)
            .limit(page_size)
            .all()
        )
        total = self.db.query(User).count()
        
        return BatchUsersOut(total=total, count=len(users), users=users).model_dump()

    def create_user(self, user_data: UserCreate) -> UserOut:
        user = User(**user_data.dict())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserOut.model_validate(user)

    def create_batch(self, users: List[UserCreate]) -> List[UserOut]:
        user_orms = [User(**u.dict()) for u in users]
        self.db.add_all(user_orms)
        self.db.commit()
        for user in user_orms:
            self.db.refresh(user)
        return [UserOut.model_validate(user) for user in user_orms]

    def update_user(self, student_id: str, user_data: UserUpdate) -> Optional[UserOut]:
        user = self.db.query(User).filter(User.student_id == student_id).first()
        if not user:
            return None
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return UserOut.model_validate(user)

    def delete_user(self, student_id: str) -> None:
        user = self.db.query(User).filter(User.student_id == student_id).first()
        if not user:
            raise ValueError(f"User with student_id {student_id} not found.")
        self.db.delete(user)
        self.db.commit()
