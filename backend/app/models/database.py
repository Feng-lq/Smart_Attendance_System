from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. 创建引擎 (Engine) - 这是连接数据库的核心
engine = create_engine(settings.DATABASE_URL)

# 2. 创建会话工厂 (SessionLocal)
# 以后每次要查数据库，就从这里拿一个 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 创建基类 (Base)
# 以后所有的表模型(User, Student)都要继承这个 Base
Base = declarative_base()

# 4. 获取数据库会话的依赖函数 (给 FastAPI 用的)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()