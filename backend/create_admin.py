from app.models.database import SessionLocal
from app.models.sql_models import User
from app.core import security

def create_admin():
    db = SessionLocal()
    username = "admin"
    password = "123456"
    
    # 这里会去查数据库，如果表结构对了，这里就不会报错了
    user = db.query(User).filter(User.username == username).first()
    if user:
        print("管理员已存在。")
        return

    hashed_pw = security.get_password_hash(password)
    
    # 这里的参数必须和 sql_models.py 里的 User 类字段一模一样
    new_user = User(
        username=username, 
        hashed_password=hashed_pw,
        email="admin@example.com" # 👈 确保这里有 email，且模型里也有
    )
    
    db.add(new_user)
    db.commit()
    print("✅ 管理员创建成功！")

if __name__ == "__main__":
    create_admin()