from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/BookHub"


engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 获取 db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()