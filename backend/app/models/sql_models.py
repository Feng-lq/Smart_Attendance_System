from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.models.database import Base

# 1. Admin User Table (Used for website login)
# 1. 管理员表 (用于登录网站)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # Username
    # 用户名
    username = Column(String, unique=True, index=True) 
    # Hashed password (Never store plain text!)
    # 加密后的密码 (千万别存明文!)
    hashed_password = Column(String) 
    email = Column(String, nullable=True)

# 2. Class Table (To differentiate class rosters)
# 2. 班级表 (用于区分不同班级的名单)
class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    # Class name, e.g., "CS101"
    # 班级名称，如 "CS101"
    name = Column(String, unique=True, index=True) 
    
    # Establish relationship with students: One class has many students (One-to-Many)
    # 建立与学生的关联：一个班级有多个学生 (一对多)
    students = relationship("Student", back_populates="student_class", cascade="all, delete-orphan")

    # Relate to attendance sessions: One class has multiple attendance records
    # 关联考勤批次：一个班级有很多次考勤记录
    sessions = relationship("AttendanceSession", back_populates="clazz", cascade="all, delete-orphan")

# 3. Student Table 
# 3. 学生表 
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    # Student ID (Matriculation Number)
    # 学号
    student_id = Column(String, unique=True, index=True) 
    name = Column(String)
    # Used for sending absence notification emails
    # 用于发送缺勤提醒邮件
    email = Column(String, nullable=True) 
    # Student login password (stored as ciphertext)
    # 学生登录密码 (加密存储)
    hashed_password = Column(String, nullable=True)
    
    # Foreign Key: Link to the id in classes table
    # 外键：关联到 classes 表的 id
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # Store relative path of the face photo
    # 存储人脸照片相对路径
    photo_path = Column(String) 
    
    # Store 128D face feature vector (JSON string)
    # 存储 128维人脸特征向量 (JSON字符串)
    face_encoding = Column(Text, nullable=True) 

    # Reverse relationship with Class
    # 建立与班级的反向关联
    student_class = relationship("Class", back_populates="students")
    # Relationship with attendance records
    # 建立与考勤记录的关联
    attendance_records = relationship("AttendanceRecord", back_populates="student")

# 4. Attendance Session Table (Core table: records overall status of a specific class session)
# 4. 考勤批次表 (核心表：记录某节课的整体情况)
class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"

    # Use String to store UUID to prevent filename conflicts
    # 使用 String 存储 UUID，防止文件名冲突
    id = Column(String, primary_key=True, index=True) 
    
    class_id = Column(Integer, ForeignKey("classes.id"))
    
    # Record creation timestamp
    # 记录创建时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 🚀 Core fields: Image evidence paths (Relative paths, e.g., /static/history/xxx.jpg)
    # 🚀 核心字段：图片凭证路径 (存相对路径，如 /static/history/xxx.jpg)
    original_image_path = Column(String, nullable=True)  # Original uploaded group photo / 原始上传的大合照
    annotated_image_path = Column(String, nullable=True) # Recognition result with bounding boxes / 画了框的识别结果图
    
    # 🚀 Core fields: Statistics cache (Directly stored for fast history queries)
    # 🚀 核心字段：统计缓存 (为了历史列表查询飞快，直接存结果)
    present_count = Column(Integer, default=0)
    absent_count = Column(Integer, default=0)

    # Relationships
    # 关联
    clazz = relationship("Class", back_populates="sessions")
    # One session contains multiple specific student records
    # 一个批次包含多条具体的学生记录
    records = relationship("AttendanceRecord", back_populates="session", cascade="all, delete-orphan")

# 5. Attendance Record Table (Records individual student status in a session)
# 5. 考勤明细表 (记录每个学生在该批次的状态)
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    
    # Link to the Session table above
    # 关联到上面的 Session 表
    session_id = Column(String, ForeignKey("attendance_sessions.id"))
    
    # Link to the Student table
    # 关联到学生
    student_id = Column(Integer, ForeignKey("students.id"))
    
    # Status: "present" or "absent"
    # 状态: "present" 或 "absent"
    status = Column(String) 
    
    # Establish relationships
    # 建立关联
    session = relationship("AttendanceSession", back_populates="records")
    student = relationship("Student", back_populates="attendance_records")