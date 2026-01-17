from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.models import sql_models, database  # 导入数据库模型和 get_db
from app.core import security               # 导入你的 Token 处理逻辑

# 1. 创建路由对象
router = APIRouter(tags=["Authentication"])

# 2. 迁移登录逻辑
@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_db)  # 👈 注意：这里改为引用 database.py 里的 get_db
):
    # 查询用户
    user = db.query(sql_models.User).filter(sql_models.User.username == form_data.username).first()
    
    # 验证用户是否存在以及密码是否匹配
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="用户名或密码错误"
        )
    
    # 生成 JWT Access Token
    access_token = security.create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }