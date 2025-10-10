from typing import Protocol, Optional, List, Union, Dict
from app.schemas.user import UserCreate, UserUpdate, UserOut

class IUserRepository(Protocol):
    def get_user_by_uid(self, uid: int) -> Optional[UserOut]:
        ...

    def get_user_by_student_id(self, student_id: str) -> Optional[UserOut]: 
        ...
    
    def get_batch_users(self, page: int, page_size: int) -> List[UserOut]: 
        ...
    
    def create_user(self, user_data: UserCreate) -> UserOut: 
        ...


    def create_batch(self, users: List[UserCreate]) -> List[UserOut]: 
        ...
    
    
    def update_user(self, student_id: str, user_data: UserUpdate) -> Optional[UserOut]: 
        ...
    
    def delete_user(self, student_id: str) -> None: 
        ...
