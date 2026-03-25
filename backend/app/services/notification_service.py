# backend/app/services/notification_service.py
from typing import List, Set
from fastapi import BackgroundTasks
from app.core.email import send_absent_notification
from app.models import sql_models

class NotificationService:
    
    @staticmethod
    def notify_absent_students(
        background_tasks: BackgroundTasks, 
        all_students: List[sql_models.Student], 
        present_student_ids: Set[int], 
        class_name: str
    ) -> int:
        """
        Calculate absent students and trigger email notifications in the background.
        计算缺勤学生并在后台触发邮件通知。
        """
        # 1. Filter students who are absent and have a valid email address
        # 1. 筛选出缺勤且有邮箱的学生 
        absent_emails = [
            student.email 
            for student in all_students 
            if student.id not in present_student_ids and student.email
        ]
        
        # 2. If there are absentees, add the email sending task to the background queue
        # 2. 如果有缺勤者，将发送邮件任务添加到后台任务队列
        if absent_emails:
            print(f"📨 [Notification] Preparing to send emails to {len(absent_emails)} student(s)")
            background_tasks.add_task(send_absent_notification, absent_emails, class_name)
            return len(absent_emails)
            
        return 0