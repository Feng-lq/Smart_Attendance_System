# backend/app/services/auth_service.py
from sqlalchemy.orm import Session
from app.models import sql_models
from app.core import security 
from jose import jwt, JWTError
from app.core.config import settings

class AuthService:
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str, role: str):
        """
        Core business logic: Query different tables based on role and verify password
        核心业务逻辑：根据角色去查不同的表，并验证密码
        :return: User/Student object (Success) or None (Failure)
        """
        # === Scenario A: Admin/Instructor Login ===
        # === 场景 A: 管理员/教师登录 ===
        if role == 'admin':
            user = db.query(sql_models.User).filter(sql_models.User.username == username).first()
            if not user:
                return None
            
            # Verify password
            # 验证密码
            if not security.verify_password(password, user.hashed_password):
                return None
            
            return user
            
        # === Scenario B: Student Login ===
        # === 场景 B: 学生登录 ===
        elif role == 'student':
            # Students log in using their student_id as the username
            # 学生用学号 (student_id) 登录
            student = db.query(sql_models.Student).filter(sql_models.Student.student_id == username).first()
            if not student:
                return None
            
            # Special logic: If the student hasn't set a password yet (NULL in database)
            # 特殊逻辑：如果学生还没设置过密码 (数据库里是 NULL)
            if not student.hashed_password:
                # Allow using the default password "123456"
                # 允许使用默认密码 "123456"
                if password == "123456":
                    return student  
                else:
                    return None
            
            # Standard verification (Encrypted password exists in database)
            # 常规验证 (数据库里有加密密码)
            if not security.verify_password(password, student.hashed_password):
                return None
            
            return student
            
        return None

    # ==========================================
    # === Proxy Methods / 代理机制与鉴权工具 ===
    # ==========================================
    
    @staticmethod
    def create_token(data: dict):
        """
        Proxy call to security module to generate Token
        透传调用 security 生成 Token
        """
        return security.create_access_token(data)

    # Renamed to match the call in auth.py
    # 重命名为 get_password_hash，与路由层的调用强绑定
    @staticmethod
    def get_password_hash(password: str):
        """
        Proxy call to security module to encrypt password
        透传调用 security 加密密码
        """
        return security.get_password_hash(password)

    # Added decode_token to support Zero-Trust password update
    # 新增 decode_token，支撑零信任架构下的密码修改逻辑
    @staticmethod
    def decode_token(token: str) -> dict | None:
        """
        Decode and verify JWT Token.
        解析并校验 JWT Token。
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            # Token is expired or invalid
            # 凭证过期或被篡改，静默返回 None
            return None