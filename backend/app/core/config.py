import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Smart Attendance System"
    # 读取数据库链接，如果读取失败(比如没创建.env)，就给个默认值防止报错
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/fyp_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key")

settings = Settings()