# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# =======================
# 1. Authentication Related
# 1. 认证相关
# =======================

class Token(BaseModel):
    access_token: str
    token_type: str
    # Return role info (admin/student)
    # 返回角色信息 (admin/student)
    role: str  

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class LoginRequest(BaseModel):
    """
    Used to receive JSON login requests from the frontend.
    用于接收前端的 JSON 登录请求。
    """
    username: str = Field(..., description="Login username or student ID", examples=["admin", "2024001"])
    password: str = Field(..., description="Login password", examples=["123456"])
    # Default is admin login, can also be "student"
    # 默认为管理员登录，也可以是 "student"
    role: str = Field(default="admin", description="Role identity", examples=["admin", "student"])  

# =======================
# 2. Class Related
# 2. 班级相关
# =======================

class ClassBase(BaseModel):
    name: str = Field(..., description="Class name", examples=["CS101"])

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id: int
    
    class Config:
        # Allow reading data from SQLAlchemy ORM models
        # 允许从 SQLAlchemy 模型读取数据
        from_attributes = True 

# =======================
# 3. Student Related
# 3. 学生相关
# =======================

class StudentBase(BaseModel):
    name: str = Field(..., description="Student's real name", examples=["John Doe"])
    student_id: str = Field(..., description="Student ID", examples=["STU2024001"])
    class_id: int = Field(..., description="Class ID", examples=[1])
    email: str | None = Field(default=None, description="Email for absence notifications", examples=["test@qq.com"])

class StudentCreate(StudentBase):
    """
    Used when creating/registering a new student.
    创建学生时使用。
    """
    # Allow setting password during registration (if not provided, backend defaults to 123456)
    # 允许在录入时设置密码 (如果不填，后端逻辑默认为 123456)
    password: str | None = Field(default=None, description="Initial password", examples=["123456"]) 

class Student(StudentBase):
    """
    Student info returned to the frontend.
    返回给前端的学生信息。
    """
    id: int
    photo_path: str | None = None 
    
    class Config:
        from_attributes = True

# =======================
# 4. Notification Related
# 4. 考勤通知相关
# =======================

class NotifyRequest(BaseModel):
    """
    Used to receive frontend requests for manual email sending.
    用于接收前端手动发送邮件的请求。
    """
    session_id: str = Field(..., description="Attendance session UUID", examples=["a8f9c2d1-..."])

# =======================
# 5. Attendance History/Session Related
# 5. 考勤历史相关
# =======================

class AttendanceRecordBase(BaseModel):
    student_id: int
    status: str = Field(..., description="Attendance status", examples=["present", "absent"])
    timestamp: datetime

class AttendanceSessionOut(BaseModel):
    id: str
    class_name: str
    created_at: str
    present_count: int
    absent_count: int
    total_count: int
    attendance_rate: float
    
    # Allow null to prevent errors on older data without images
    # 允许为空，防止某些旧数据没有图片报错
    original_img: str | None = None
    result_img: str | None = None
    
    # Core fix: Add roster list fields
    # 核心修复：添加名单列表字段 
    present_students: List[Student] = [] 
    absent_students: List[Student] = []
    total_faces_detected: int = 0
    
    class Config:
        from_attributes = True