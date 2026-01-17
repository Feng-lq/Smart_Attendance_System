# backend/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. 导入数据库配置与 ORM 模型
from app.models import database, sql_models
# 2. 导入各个功能模块的路由
from app.api import auth, classes, students, attendance, analytics
# 🟢 在应用启动时，自动在 PostgreSQL 中创建所有尚未存在的表
# 这是毕设演示时最稳妥的做法，确保数据库结构与代码同步
sql_models.Base.metadata.create_all(bind=database.engine)

# 初始化 FastAPI 实例
app = FastAPI(
    title="Smart Class Attendance System",
    description="基于 FastAPI + PostgreSQL + Face_Recognition 的智能考勤系统后端",
    version="1.0.0"
)

# 3. 静态资源目录初始化与挂载
# 确保项目根目录下存在 static/uploads (学生证件照) 和 static/group_photos (考勤合照)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/group_photos", exist_ok=True)

# 挂载静态文件夹，前端可以通过 http://127.0.0.1:8000/static/... 直接访问图片
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. 跨域资源共享 (CORS) 配置
# 允许 Vue 前端（通常在 5173 端口）跨域访问后端接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境建议指定具体域名如 ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. 注册模块化路由
# 统一增加 /api 前缀，这符合你 web_client 里的 api 调用路径规范
app.include_router(auth.router, prefix="/api")       # 包含 /token 接口
app.include_router(classes.router, prefix="/api")    # 包含 /classes 接口
app.include_router(students.router, prefix="/api")   # 包含 /students 接口
app.include_router(attendance.router, prefix="/api") # 包含 /attendance/class_photo 接口
app.include_router(analytics.router, prefix="/api")

# 根路径测试接口
@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Smart Attendance System API is running",
        "database": "PostgreSQL Connected"
    }

# 运行提示：
# 在 backend 目录下执行命令：uvicorn main:app --reload