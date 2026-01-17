# backend/reset_db.py
from sqlalchemy import text
from app.models.database import engine, Base
# 必须导入 sql_models，这样 Base 才知道新表结构
from app.models import sql_models 
from app.core import security

def reset_database():
    print("⚠️  正在执行数据库全量重置...")
    
    # === 1. 关键修复：手动清理旧的僵尸表 ===
    # 因为 python 代码里已经删除了 AttendanceLog 类，
    # 所以 drop_all 不会自动删除 attendance_logs 表，必须手动删！
    with engine.connect() as conn:
        print("正在强制清理残留的旧表 (attendance_logs)...")
        # 使用 CASCADE 级联删除，忽视外键约束
        conn.execute(text("DROP TABLE IF EXISTS attendance_logs CASCADE"))
        # 如果还有其他旧表删不掉，也可以加在这里，例如:
        # conn.execute(text("DROP TABLE IF EXISTS old_table_name CASCADE"))
        conn.commit()

    # === 2. 暴力删除剩余所有表 ===
    # 现在 attendance_logs 没了，students 就可以被正常删除了
    print("正在清除剩余数据表...")
    Base.metadata.drop_all(bind=engine)
    
    # === 3. 重新创建所有新表 ===
    print("正在创建新表结构...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ 数据库表结构重置完成！(users, classes, students, attendance_sessions, attendance_records)")

def init_admin_user():
    print("正在初始化管理员账号...")
    from sqlalchemy.orm import Session
    from app.models import sql_models
    
    # 手动创建会话
    db = Session(bind=engine)
    
    try:
        # 检查是否已存在
        user = db.query(sql_models.User).filter(sql_models.User.username == "admin").first()
        if not user:
            # 创建默认管理员: admin / 123456
            hashed_pw = security.get_password_hash("123456")
            # 注意：确保 email 字段存在于 sql_models.User 中
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
        print(f"创建管理员失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    try:
        # 执行重置
        reset_database()
        # 初始化管理员
        init_admin_user()
    except Exception as e:
        print(f"❌ 发生错误: {e}")