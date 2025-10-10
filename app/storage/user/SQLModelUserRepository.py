from sqlmodel import Session, select
from typing import Optional, List
from app.models.user import User  
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.storage.user.user_interface import IUserRepository


# SQLModel ORM 模型与 Pydantic 模型无需经过一层转化，直接使用 SQLModel 模型即可 (以下代码未经过测试, 有待验证)
class SQLModelUserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_uid(self, uid: int) -> Optional[UserOut]:
        user = self.db.get(User, uid)
        return UserOut.model_validate(user) if user else None

    def get_user_by_student_id(self, student_id: str) -> Optional[UserOut]:
        statement = select(User).where(User.student_id == student_id)
        result = self.db.exec(statement).first()
        return UserOut.model_validate(result) if result else None

    def get_batch_users(self, page: int, page_size: int) -> List[UserOut]:
        statement = select(User).offset(page * page_size).limit(page_size)
        results = self.db.exec(statement).all()
        return [UserOut.model_validate(user) for user in results]

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
        statement = select(User).where(User.student_id == student_id)
        user = self.db.exec(statement).first()
        if not user:
            return None
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return UserOut.model_validate(user)

    def delete_user(self, student_id: str) -> None:
        statement = select(User).where(User.student_id == student_id)
        user = self.db.exec(statement).first()
        if not user:
            raise ValueError(f"User with student_id {student_id} not found.")
        self.db.delete(user)
        self.db.commit()
