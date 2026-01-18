# backend/app/core/email.py
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List
import os

# 📧 邮件配置
# 建议：实际生产中应该从 .env 读取，这里为了方便演示先写在代码里
# 如果你使用了 .env，可以用 os.getenv("MAIL_USERNAME") 替换
conf = ConnectionConfig(
    MAIL_USERNAME = "你的邮箱@qq.com",        # 🔴 请替换!
    MAIL_PASSWORD = "你的授权码",             # 🔴 请替换! (QQ邮箱是授权码，不是QQ密码)
    MAIL_FROM = "你的邮箱@qq.com",            # 🔴 请替换!
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.qq.com",            # 如果用 Gmail 改为 smtp.gmail.com
    MAIL_STARTTLS = False, 
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_absent_notification(email_list: List[str], class_name: str):
    """
    发送缺勤通知邮件
    """
    if not email_list:
        return

    html = f"""
    <h3>考勤缺勤通知</h3>
    <p>亲爱的同学：</p>
    <p>系统检测到您在刚刚结束的 <strong>{class_name}</strong> 课程考勤中被标记为 <strong>缺勤 (Absent)</strong>。</p>
    <p>如果您确实在教室，请课后联系任课老师进行补签。</p>
    <br>
    <p><em>此邮件由智慧考勤系统自动发送，请勿回复。</em></p>
    """

    message = MessageSchema(
        subject=f"【警报】{class_name} 课程缺勤通知",
        recipients=email_list,
        body=html,
        subtype=MessageType.html
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        print(f"✅ [Email] 邮件发送成功，共发送给 {len(email_list)} 人")
    except Exception as e:
        print(f"❌ [Email] 邮件发送失败: {e}")