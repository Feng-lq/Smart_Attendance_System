from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.models.database import Base
# 1. 管理员表 (用于登录网站)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # 用户名
    hashed_password = Column(String) # 加密后的密码 (千万别存明文!)
    email = Column(String, nullable=True)

# 2. 班级表 (新需求：用于区分不同班级的名单)
class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # 班级名称，如 "CS101"
    
    # 建立与学生的关联：一个班级有多个学生
    students = relationship("Student", back_populates="student_class", cascade="all, delete-orphan")

    # 关联考勤批次 (新)：一个班级有很多次考勤记录
    sessions = relationship("AttendanceSession", back_populates="clazz", cascade="all, delete-orphan")

# 3. 学生表 (修改：增加了 class_id 关联)
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, index=True) # 学号
    name = Column(String)
    email = Column(String, nullable=True) # 用于发送缺勤提醒邮件
    
    # 外键：关联到 classes 表的 id
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # 存储人脸照片路径
    photo_path = Column(String) 
    
    # 存储 128维人脸特征向量 (JSON字符串)
    face_encoding = Column(Text, nullable=True) 

    # 建立与班级的反向关联
    student_class = relationship("Class", back_populates="students")
    # 建立与考勤记录的关联
    attendance_records = relationship("AttendanceRecord", back_populates="student")

# 4. [新增] 考勤批次表 (核心表：记录某节课的整体情况)
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    # 使用 String 存储 UUID，防止文件名冲突
    id = Column(String, primary_key=True, index=True) 
    
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # 记录创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 🚀 核心字段：图片凭证路径 (存相对路径，如 /static/history/xxx.jpg)
    original_image_path = Column(String, nullable=True)  # 原始上传的大合照
    annotated_image_path = Column(String, nullable=True) # 画了框的识别结果图
    
    # 🚀 核心字段：统计缓存 (为了历史列表查询飞快，直接存结果)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)

    # 关联
    clazz = relationship("Class", back_populates="sessions")
    # 一个批次包含多条具体的学生记录
    records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")

# 5. [重构] 考勤明细表 (记录每个学生在该批次的状态)
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # 关联到上面的 Session 表
    session_id = Column(String, ForeignKey("attendance_sessions.id"))
    
    # 关联到学生
    student_id = Column(Integer, ForeignKey("students.id"))
    
    # 状态: "present" 或 "absent"
    status = Column(String) 
    
    # 建立关联
    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("Student", back_populates="attendance_records")