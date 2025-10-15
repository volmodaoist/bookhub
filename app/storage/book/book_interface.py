from typing import Protocol, Optional, List, Union
from app.schemas.book import BookRetrieveReq, BookOut, BatchBooksOut, BookUpdate, BookCreate


class IBookRepository(Protocol):
    # 基础读取
    def get_by_bid(self, bid: int) -> Optional[BookOut]: 
        ...
    
    def get_by_isbn(self, isbn: str) -> Optional[BookOut]: 
        ...

    # 复杂检索（分页/排序/过滤/模糊）
    def search_book(self, req: BookRetrieveReq) -> BatchBooksOut: 
        ...

    # 管理端（多读少写，依然保留）
    def create_book(self, data: BookCreate) -> BookOut: 
        ...
    
    def update_book(self, isbn: int, data: BookUpdate) -> Optional[BookOut]: 
        ...
    
    def delete_book(self, isbn: int) -> Optional[BookOut]: 
        ...