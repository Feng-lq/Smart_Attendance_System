# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# =======================
# 1. 认证相关 (Authentication)
# =======================

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str  # 返回角色信息 (admin/student)

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class LoginRequest(BaseModel):
    """
    用于接收前端的 JSON 登录请求
    """
    username: str
    password: str
    role: str = "admin"  # 默认为管理员登录，也可以是 "student"

# =======================
# 2. 班级相关 (Class)
# =======================

class ClassBase(BaseModel):
    name: str

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id: int
    
    class Config:
        from_attributes = True # 允许从 SQLAlchemy 模型读取数据

# =======================
# 3. 学生相关 (Student)
# =======================

class StudentBase(BaseModel):
    name: str
    student_id: str
    class_id: int
    email: str | None = None

class StudentCreate(StudentBase):
    """
    创建学生时使用
    """
    # 允许在录入时设置密码 (如果不填，后端会在逻辑里设为默认 123456)
    password: str | None = None 

class Student(StudentBase):
    """
    返回给前端的学生信息
    """
    id: int
    photo_path: str | None = None # 确保这里有，否则学生头像出不来
    
    class Config:
        from_attributes = True

# =======================
# 4. 考勤通知相关 (Notification)
# =======================

class NotifyRequest(BaseModel):
    """
    用于接收前端手动发送邮件的请求
    """
    session_id: str

# =======================
# 5. 考勤历史相关 (History/Session)
# =======================

class AttendanceRecordBase(BaseModel):
    student_id: int
    status: str
    timestamp: datetime

class AttendanceSessionOut(BaseModel):
    id: str
    class_name: str
    created_at: str
    present_count: int
    absent_count: int
    total_count: int
    attendance_rate: float
    
    # 允许为空，防止某些旧数据没有图片报错
    original_img: str | None = None
    result_img: str | None = None
    
    # 核心修复：添加名单列表字段 
    present_students: List[Student] = [] 
    absent_students: List[Student] = []
    total_faces_detected: int = 0
    
    class Config:
        from_attributes = True