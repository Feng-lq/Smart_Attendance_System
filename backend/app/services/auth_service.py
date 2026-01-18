# backend/app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models import sql_models
from app.core import security 

class AuthService:
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str, role: str):
        """
        核心业务逻辑：根据角色去查不同的表，并验证密码
        :return: User/Student 对象 (成功) 或 None (失败)
        """
        # === 场景 A: 管理员/教师登录 ===
        if role == 'admin':
            user = db.query(sql_models.User).filter(sql_models.User.username == username).first()
            if not user:
                return None
            
            # 验证密码
            if not security.verify_password(password, user.hashed_password):
                return None
            
            return user
            
        # === 场景 B: 学生登录 ===
        elif role == 'student':
            # 学生用学号 (student_id) 登录
            student = db.query(sql_models.Student).filter(sql_models.Student.student_id == username).first()
            if not student:
                return None
            
            # 特殊逻辑：如果学生还没设置过密码 (数据库里是 NULL)
            if not student.hashed_password:
                # 允许使用默认密码 "123456"
                if password == "123456":
                    return student  # 🔥 核心修复：必须返回 student 对象，不能返回 True！
                else:
                    return None
            
            # 常规验证 (数据库里有加密密码)
            if not security.verify_password(password, student.hashed_password):
                return None
            
            return student
            
        return None

    # === 代理方法 ===
    
    @staticmethod
    def create_token(data: dict):
        """透传调用 security 生成 Token"""
        return security.create_access_token(data)

    @staticmethod
    def hash_password(password: str):
        """透传调用 security 加密密码"""
        return security.get_password_hash(password)