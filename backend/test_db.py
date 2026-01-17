from sqlalchemy import text
from app.models.database import engine

try:
    # 尝试连接数据库
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 'Hello PostgreSQL!'"))
        print("\n✅✅✅ 成功连接到数据库！✅✅✅\n")
        print(f"数据库返回消息: {result.scalar()}")
except Exception as e:
    print("\n❌❌❌ 连接失败！❌❌❌\n")
    print(f"错误信息: {e}")
    print("\n检查建议：")
    print("1. 密码是不是写错了？")
    print("2. pgAdmin 里确认 fyp_db 创建了吗？")