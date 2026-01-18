# backend/app/services/notification_service.py
from typing import List
from fastapi import BackgroundTasks
from app.core.email import send_absent_notification
from app.models import sql_models

class NotificationService:
    @staticmethod
    def notify_absent_students(
        background_tasks: BackgroundTasks, 
        all_students: List[sql_models.Student], 
        present_student_ids: set, 
        class_name: str
    ):
        """
        计算缺勤学生并发送邮件
        """
        # 1. 筛选出缺勤且有邮箱的学生
        absent_emails = []
        for student in all_students:
            if student.id not in present_student_ids and student.email:
                absent_emails.append(student.email)
        
        # 2. 如果有缺勤者，添加到后台任务队列
        if absent_emails:
            print(f"📨 [Notification] 准备发送邮件给: {len(absent_emails)} 人")
            background_tasks.add_task(send_absent_notification, absent_emails, class_name)
            return len(absent_emails)
        
        return 0