# backend/reset_db.py
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models.database import engine, Base
# 必须导入 sql_models，这样 Base 才知道新表结构
from app.models import sql_models 
from app.core import security

def reset_database():
    print("⚠️  正在执行数据库全量重置...")
    
    # === 1. 清理可能残留的旧表 ===
    with engine.connect() as conn:
        print("正在清理残留表...")
        # 强制删除可能存在的旧表，防止外键冲突
        conn.execute(text("DROP TABLE IF EXISTS attendance_records CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS attendance_sessions CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS students CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS classes CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS attendance_logs CASCADE")) # 清理更早版本的旧表
        conn.commit()

    # === 2. 暴力删除剩余所有表 (双重保险) ===
    print("正在清除 SQLAlchemy 元数据...")
    Base.metadata.drop_all(bind=engine)
    
    # === 3. 重新创建所有新表 ===
    print("正在创建新表结构...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ 数据库表结构重置完成！")

def init_admin_user():
    print("正在初始化管理员账号...")
    
    # 手动创建会话
    db = Session(bind=engine)
    
    try:
        # 检查是否已存在
        user = db.query(sql_models.User).filter(sql_models.User.username == "admin").first()
        if not user:
            # 创建默认管理员: admin / 123456
            hashed_pw = security.get_password_hash("123456")
            
            admin = sql_models.User(
                username="admin", 
                hashed_password=hashed_pw,
                email="admin@example.com" 
            )
            db.add(admin)
            db.commit()
            print("✅ 管理员账号创建成功！[账号: admin, 密码: 123456]")
        else:
            print("管理员账号已存在，跳过。")
    except Exception as e:
        print(f"❌ 创建管理员失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # 1. 重置表
        reset_database()
        # 2. 创建管理员
        init_admin_user()
    except Exception as e:
        print(f"❌ 发生严重错误: {e}")