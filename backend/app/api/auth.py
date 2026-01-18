# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import database 

# ✅ 修改点 1: 精确导入，防止报错找不到 Token
from app.schemas import Token, LoginRequest 
from app.services.auth_service import AuthService

# 创建路由对象
router = APIRouter(tags=["Authentication"])

@router.post("/auth/token", response_model=Token) # 👈 直接用 Token
async def login_for_access_token(
    login_data: LoginRequest, # 👈 直接用 LoginRequest
    db: Session = Depends(database.get_db)
):
    # 1. 调用 Service 验证身份
    user_or_student = AuthService.authenticate_user(
        db, 
        login_data.username, 
        login_data.password, 
        login_data.role
    )
    
    if not user_or_student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名、密码错误或角色不匹配",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. 准备 Token 数据
    identifier = ""
    uid = 0
    
    if login_data.role == "admin":
        identifier = user_or_student.username
        uid = user_or_student.id
    else:
        identifier = user_or_student.student_id
        uid = user_or_student.id

    # 3. 生成 Token
    # ✅ 修改点 2: 确认方法名！
    # 如果你的 AuthService 里写的是 create_token，这里必须一致。
    # 我们之前写的 Service 代理方法叫 create_token，所以这里改为 create_token。
    access_token = AuthService.create_token(
        data={
            "sub": str(identifier), 
            "role": login_data.role,
            "uid": str(uid)
        }
    )
    
    # 4. 返回结果
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": login_data.role 
    }