from fastapi import Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from app.storage.user.SQLAlchemyUserRepository import SQLAlchemyUserRepository


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/BookHub"


engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 获取 db session, 此处我只使用了 SQLAlchemy session, 未来应该读取配置根据配置信息选择使用哪个数据库工具
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 未来可以根据配置切换不同的实现
def get_user_repo(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    return SQLAlchemyUserRepository(db)