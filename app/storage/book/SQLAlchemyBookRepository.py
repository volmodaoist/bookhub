# app/storage/book/sqlalchemy_repo.py
from typing import Optional, List
from sqlalchemy.orm import Session
from app.schemas.book import (
    BookRetrieveReq, BookCreate, BookUpdate, 
    BookOut, BatchBooksOut
)
from app.storage.book.book_interface import IBookRepository
from app.models.book import Book
from app.core.db import transaction


class SQLAlchemyBookRepository(IBookRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def query_book(self, isbn: str) -> Optional[Book]:
        return self.db.query(Book).filter(Book.isbn == isbn).first()

    def get_by_bid(self, bid: int) -> Optional[BookOut]:
        book = self.db.get(Book, bid)
        return BookOut.model_validate(book) if book else None

    def get_by_isbn(self, isbn: str) -> Optional[BookOut]:
        book = self.query_book(isbn)
        return BookOut.model_validate(book) if book else None

    def search_book(self, req: BookRetrieveReq):
        pass

    def create_book(self, book_data: BookCreate) -> Optional[BookOut]:
        book = Book(**book_data.dict())

        with transaction(self.db):
            self.db.add(book)
        
        self.db.refresh(book)
        return BookOut.model_validate(book).model_dump() if book else None

    def update_book(self, isbn: str, book_data: BookUpdate) -> Optional[BookOut]:
        book = self.query_book(isbn)
        
        if not book:
            return None
        
        with transaction(self.db):
            for field, value in book_data.dict(exclude_unset=True).items():
                setattr(book, field, value)

        self.db.refresh(book)
        return BookOut.model_validate(book).model_dump() if book else None

    def delete_book(self, isbn: str) -> Optional[BookOut]:
        book = self.query_book(isbn)
        if not book: 
            raise ValueError(f"Book with isbn {isbn} not found.")
        
        with transaction(self.db):
            book_info = BookOut.model_validate(book).model_dump()
            self.db.delete(book)
    
        return book_info
        
