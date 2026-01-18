# backend/app/core/config.py
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Smart Attendance System"
    
    # 读取数据库链接
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fyp_db")
    
    # JWT 密钥 (生产环境务必修改 .env)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_for_dev_only")
    
    # 加密算法配置
    ALGORITHM: str = "HS256"
    
    # Token 过期时间 (分钟)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()