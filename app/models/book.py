from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Book(Base):
    """ 图书数据库模型，用于表示每本书的基本信息、库存量以及所在区域等信息。
    """
    __tablename__ = "books"

    bid = Column(Integer, primary_key=True, index=True)  # 图书 ID，主键，自增
    title = Column(String, nullable=False)               # 书名（必填）
    author = Column(String, nullable=False)              # 作者（必填）
    isbn = Column(String, unique=True, nullable=False)   # 国际标准书号，唯一（必填）
    stock = Column(Integer, default=0)                   # 库存数量，默认 0
    abstract = Column(String, nullable=True)             # 图书简介（可为空）

    area = Column(String, nullable=True)                 # 所在区域（如 A-Z 区）
    floor = Column(String, nullable=True)                # 所在楼层（如 1F, 2F）

    tags = Column(String, nullable=True)                 # 图书标签（多个标签用逗号分隔，例如：文学,历史,科幻）
