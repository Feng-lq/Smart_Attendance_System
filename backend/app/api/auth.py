# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models import database 

from app.schemas import Token, LoginRequest 
from app.services.auth_service import AuthService

# Create router object
# 创建路由对象
router = APIRouter(tags=["Authentication"])

# Initialize HTTPBearer to automatically extract Token from headers
# 初始化 HTTPBearer，用于自动从请求头中提取 Bearer Token
security = HTTPBearer()

# Define Pydantic schema for password update request
# 专门为密码修改定义的请求载荷模型
class PasswordUpdateRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/auth/token", response_model=Token)
async def login_for_access_token(
    login_data: LoginRequest,
    db: Session = Depends(database.get_db)
):
    # 1. Call Service to authenticate user
    # 1. 调用 Service 验证身份
    user_or_student = AuthService.authenticate_user(
        db, 
        login_data.username, 
        login_data.password, 
        login_data.role
    )
    
    if not user_or_student:
        # Return standard HTTP 401 error if authentication fails
        # 如果验证失败，则抛出标准的 HTTP 401 错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, password, or role mismatch / 账号、密码或角色不匹配", 
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Prepare Token payload data
    # 2. 准备 Token 数据
    identifier = ""
    uid = 0
    
    if login_data.role == "admin":
        identifier = user_or_student.username
        uid = user_or_student.id
    else:
        identifier = user_or_student.student_id
        uid = user_or_student.id

    # 3. Generate Access Token
    # 3. 生成 Token
    access_token = AuthService.create_token(
        data={
            "sub": str(identifier), 
            "role": login_data.role,
            "uid": str(uid)
        }
    )
    
    # 4. Return formatted result
    # 4. 返回结果
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": login_data.role 
    }

# ==========================================
# Password Update Endpoint
# 安全的密码修改通道
# ==========================================
@router.put("/auth/password")
async def update_password(
    update_data: PasswordUpdateRequest,
    db: Session = Depends(database.get_db),
    token_auth: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Securely update user password with Zero-Trust architecture.
    基于零信任架构的密码修改接口。
    """
    # 1. Extract and verify JWT Token (Prevents IDOR / 彻底防止越权访问)
    # 解析前端传来的 Token 凭证
    payload = AuthService.decode_token(token_auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token invalid or expired"
        )
        
    user_role = payload.get("role")
    username = payload.get("sub") # Sub 中存储的就是真实的学号或 Admin 账号
    
    # 2. Verify OLD password using existing auth flow
    # 2. 验证【旧密码】是否正确 
    user = AuthService.authenticate_user(db, username, update_data.old_password, user_role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect current password"
        )
        
    # 3. Hash NEW password and persist to database
    # 3. 将【新密码】进行强哈希加密并更新至数据库
    new_hashed_password = AuthService.get_password_hash(update_data.new_password)
    
    if hasattr(user, 'password'):
        user.password = new_hashed_password
    elif hasattr(user, 'hashed_password'):
        user.hashed_password = new_hashed_password
        
    db.commit()
    
    return {"message": "Password updated successfully"}