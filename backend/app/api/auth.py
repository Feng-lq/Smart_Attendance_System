# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import database 

from app.schemas import Token, LoginRequest 
from app.services.auth_service import AuthService

# Create router object
# 创建路由对象
router = APIRouter(tags=["Authentication"])

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
        # 如果验证失败，则抛出标准的 HTTP 401 错误（提示信息已英化）
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, password, or role mismatch", 
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