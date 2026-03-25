import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password encryption context (using bcrypt)
# 密码加密上下文 (使用 bcrypt 算法)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 1. Verify password (Plaintext vs. Hashed password)
# 1. 验证密码 (明文 vs 密文)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# 2. Generate password hash
# 2. 生成密码的哈希值
def get_password_hash(password):
    return pwd_context.hash(password)

# 3. Create Access Token (JWT)
# 3. 创建访问令牌 (JWT)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # Use timezone-aware UTC time instead of deprecated datetime.utcnow()
    # 使用具备时区意识的 UTC 时间，彻底解决 Python 3.12+ 的弃用警告
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Inject standard JWT claims for Zero Trust Architecture
    # 注入标准的 JWT 声明，符合零信任架构规范
    to_encode.update({
        "exp": expire,                          # Expiration Time / 过期时间
        "iat": now,                             # Issued At / 签发时间
        "jti": str(uuid.uuid4()),               # JWT ID / 唯一标识符，防重放攻击
        "iss": settings.PROJECT_NAME            # Issuer / 签发者身份声明
    })
    
    # Generate encoded JWT string
    # 生成加密的 JWT 字符串
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt