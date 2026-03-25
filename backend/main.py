# backend/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 1. Import database and models
# 1. 导入数据库与模型
from app.models import database, sql_models
# 2. Import routers
# 2. 导入路由
from app.api import auth, classes, students, attendance, analytics

# ==========================================
# 3. Application Lifespan Management
# 3. 应用生命周期管理 
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[System] Starting up Smart Attendance System...")
    
    # Create database tables (Kept simple for FYP)
    # 创建数据库表结构
    sql_models.Base.metadata.create_all(bind=database.engine)
    
    # Initialize necessary static directories safely during startup
    # 在启动阶段安全地初始化必要的静态目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(base_dir, "static")
    os.makedirs(os.path.join(static_dir, "avatars"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "history"), exist_ok=True)
    
    # Yield control back to FastAPI to start accepting requests
    # 释放控制权给 FastAPI，开始接收网络请求
    yield 
    
    # --- Code below runs on server shutdown ---
    # --- 下方的代码在服务器关闭时运行 ---
    print("[System] Shutting down successfully. All resources released.")

# Initialize FastAPI with the lifespan context
# 使用 lifespan 上下文初始化 FastAPI
app = FastAPI(
    title="Smart Class Attendance System",
    description="Smart Attendance System Backend based on FastAPI + PostgreSQL + Face_Recognition",
    version="1.0.0",
    lifespan=lifespan # 注入生命周期
)

# ==========================================
# 4. Static Files & Middleware Configuration
# 4. 静态文件与中间件配置
# ==========================================

# Mount static directory
# 挂载静态目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS Configuration (Kept open for smooth FYP demonstration)
# CORS 跨域配置 (保持开放以确保毕设演示顺利，无跨域阻碍)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 5. Register Routers
# 5. 注册路由
# ==========================================
app.include_router(auth.router, prefix="/api")
app.include_router(classes.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(attendance.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "System is running", "docs": "/docs"}