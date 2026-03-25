from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Create Engine - The core of the database connection
# 1. 创建引擎 (Engine) - 这是连接数据库的核心
engine = create_engine(settings.DATABASE_URL)

# 2. Create Session Factory (SessionLocal)
# A new session will be instantiated from here for every database query
# 2. 创建会话工厂 (SessionLocal) - 以后每次要查询数据库，就从这里实例化一个 session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Create Base Class (Base)
# All subsequent ORM models (e.g., User, Student) will inherit from this Base
# 3. 创建基类 (Base) - 以后所有的 ORM 表模型 (如 User, Student) 都要继承这个 Base
Base = declarative_base()

# 4. Dependency function to get the database session (for FastAPI injection)
# 4. 获取数据库会话的依赖函数 (供 FastAPI 注入使用)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()