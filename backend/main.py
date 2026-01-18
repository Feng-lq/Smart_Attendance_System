# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. 导入数据库与模型
from app.models import database, sql_models
# 2. 导入路由
from app.api import auth, classes, students, attendance, analytics

# 自动创建表结构
sql_models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Smart Class Attendance System",
    description="基于 FastAPI + PostgreSQL + Face_Recognition 的智能考勤系统后端",
    version="1.0.0"
)

# ==========================================
# 3. 静态资源配置 (🔥 核心修改点)
# ==========================================

# 获取 main.py 所在的绝对目录 (E:\Study\FYP\Smart_Attendance_System\backend)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 拼接 static 文件夹的绝对路径
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 确保文件夹存在 (跟 FileService 保持一致，建立 avatars 和 history)
os.makedirs(os.path.join(STATIC_DIR, "avatars"), exist_ok=True)
os.makedirs(os.path.join(STATIC_DIR, "history"), exist_ok=True)

# 挂载静态目录
# 访问 http://127.0.0.1:8000/static/avatars/xxx.jpg -> 映射到硬盘 backend/static/avatars/xxx.jpg
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ==========================================

# 4. CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(classes.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "System is running", "docs": "/docs"}