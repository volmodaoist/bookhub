from sqlalchemy import create_engine, text

DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/BookHub"
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        
    print(f"成功连接 MySQL 数据库!")
except Exception as e:
    print(f"数据库连接失败: {e}")
