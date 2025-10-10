from pydantic import BaseModel
from typing import Optional


# 用户检索图书一般只用到 title 参数 (有待完善)
class BookRetrieveReq(BaseModel):
    title: str
    isbn: Optional[str] = None 