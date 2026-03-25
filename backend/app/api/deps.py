# backend/app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

# Import configurations and models
# 导入配置和模型
from app.models import database, sql_models
from app.core.config import settings
from app import schemas

# Define Token retrieval scheme (corresponds to the route address in auth.py)
# 定义 Token 获取方式 (对应 auth.py 中的路由地址)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user_payload(token: str = Depends(oauth2_scheme)):
    """
    Only responsible for parsing the Token, without querying the database. Returns the payload dictionary.
    只负责解析 Token，不查数据库。返回 payload 字典。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode Token
        # 解码 Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception

async def get_current_student(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(database.get_db)
) -> sql_models.Student:
    """
    Retrieve the currently logged-in student object via Token.
    通过 Token 获取当前登录的学生对象。
    """
    role = payload.get("role")
    uid = payload.get("uid")

    # Permission validation
    # 权限校验
    if role != "student":
        # HTTP 403 represents "Forbidden" in standard RESTful semantics
        raise HTTPException(status_code=403, detail="Forbidden: Student access only")
    
    # Query database
    # 查库
    student = db.query(sql_models.Student).filter(sql_models.Student.id == uid).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student account not found")
    
    return student