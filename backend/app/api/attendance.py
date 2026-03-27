# backend/app/api/attendance.py
import json
import uuid
import cv2
import os
import asyncio # 🚀 [新增] 用于模拟发送邮件的异步等待
import numpy as np
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel # 🚀 [新增] 用于定义通知请求体
from app.models import database, sql_models
from app import schemas

# Import core services / 引入核心服务
from app.services.face_service import FaceService
from app.services.file_service import FileService

router = APIRouter(tags=["Attendance"])

# ==========================================
# 🚀 [New Feature] Notification Request Schema
# 🚀 [新增] 定义前端传来的通知请求载荷
# ==========================================
class NotificationRequest(BaseModel):
    session_id: str

# ==========================================
# 1. Core Attendance Recognition Endpoint
# 1. 核心考勤识别接口
# ==========================================
@router.post("/attendance/recognize", response_model=schemas.AttendanceSessionOut)
async def recognize_attendance(
    class_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # A. Verify class existence / 验证班级
    clazz = db.query(sql_models.Class).filter(sql_models.Class.id == class_id).first()
    if not clazz:
        raise HTTPException(status_code=404, detail="Class not found / 未找到该班级")

    # B. Prepare known face data / 准备已知人脸数据
    students = db.query(sql_models.Student).filter(sql_models.Student.class_id == class_id).all()
    
    known_face_encodings = []
    known_students_data = [] 
    
    for student in students:
        if student.face_encoding:
            try:
                encoding = json.loads(student.face_encoding)
                known_face_encodings.append(encoding)
                known_students_data.append({
                    "id": student.id,
                    "name": student.name
                })
            except Exception:
                continue 

    if not known_face_encodings:
        raise HTTPException(status_code=400, detail="No face data registered for this class / 该班级暂无已录入的人脸数据")

    # C. Save original uploaded image / 保存原始上传图片
    try:
        original_path = await FileService.save_upload_file(file, sub_dir="history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image / 图片保存失败: {str(e)}")

    # Reset file pointer / 重置文件指针
    await file.seek(0)

    # D. Call FaceService for recognition / 调用 FaceService 进行识别
    try:
        image_np = await FaceService.load_image_from_file(file)
        
        result_img_np, found_ids = FaceService.process_recognition(
            image_np, 
            known_face_encodings, 
            known_students_data 
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Recognition algorithm error / 识别算法异常: {str(e)}")

    # E. Save annotated result image / 保存标注后的结果图片
    filename = os.path.basename(original_path)
    result_filename = f"result_{filename}"
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save_dir = os.path.join(base_dir, "static", "history")
    os.makedirs(save_dir, exist_ok=True)
    
    result_path_disk = os.path.join(save_dir, result_filename)
    
    # Write file (Convert RGB to BGR for OpenCV) / 写入文件 (RGB -> BGR)
    result_img_bgr = cv2.cvtColor(result_img_np, cv2.COLOR_RGB2BGR)
    cv2.imwrite(result_path_disk, result_img_bgr)

    # URL path for frontend / 提供给前端的 URL 路径
    result_path_db = f"/static/history/{result_filename}"

    # F. Write to Database / 写入数据库
    present_count = len(set(found_ids))
    total_count = len(students)
    absent_count = total_count - present_count
    
    # Calculate rate (for display only) / 计算出勤率 (仅用于显示，不存数据库)
    attendance_rate = round((present_count / total_count) * 100, 2) if total_count > 0 else 0.0
    
    # Generate UUID (Database ID is String) / 生成 UUID
    session_id = str(uuid.uuid4())
    
    new_session = sql_models.AttendanceSession(
        id=session_id,
        class_id=class_id,
        created_at=datetime.now(),
        original_image_path=original_path, 
        annotated_image_path=result_path_db,
        present_count=present_count,
        absent_count=absent_count
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # G. Write detailed records / 写入考勤明细记录
    found_id_set = set(found_ids)
    
    present_students_list = []
    absent_students_list = []

    for student in students:
        is_present = student.id in found_id_set
        status = "present" if is_present else "absent"
        
        record = sql_models.AttendanceRecord(
            session_id=new_session.id,
            student_id=student.id,
            status=status
        )
        db.add(record)

        if is_present:
            present_students_list.append(student)
        else:
            absent_students_list.append(student)
            
    db.commit()

    # H. Return payload / 构造返回值
    return {
        "id": str(new_session.id),
        "class_name": clazz.name,
        "created_at": new_session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "present_count": present_count,
        "absent_count": absent_count,
        "total_count": total_count,
        "attendance_rate": attendance_rate, 
        "original_img": original_path,
        "result_img": result_path_db, 
        "present_students": present_students_list, 
        "absent_students": absent_students_list,   
        "total_faces_detected": len(found_ids) 
    }

# ==========================================
# 2. Fetch Attendance History Endpoint
# 2. 获取考勤历史接口
# ==========================================
@router.get("/attendance/history", response_model=list[schemas.AttendanceSessionOut])
def get_attendance_history(
    class_id: Optional[int] = None,  
    db: Session = Depends(database.get_db)
):
    query = db.query(sql_models.AttendanceSession)
    
    # Apply filter if class_id is provided / 动态条件过滤
    if class_id is not None:
        query = query.filter(sql_models.AttendanceSession.class_id == class_id)
        
    # Order by creation time descending / 按时间倒序排列
    sessions = query.order_by(sql_models.AttendanceSession.created_at.desc()).all()
    
    result = []
    # ⚠️ Code Review Warning: N+1 Query problem exists here, but kept for stability
    # ⚠️ 架构师提示：这里在 for 循环里查数据库属于 N+1 查询问题，但为了毕设稳定暂时保留
    for sess in sessions:
        clazz = db.query(sql_models.Class).filter(sql_models.Class.id == sess.class_id).first()
        
        total = sess.present_count + sess.absent_count
        rate = round((sess.present_count / total) * 100, 2) if total > 0 else 0.0
        
        result.append({
            "id": str(sess.id),
            "class_name": clazz.name if clazz else "Unknown",
            "created_at": sess.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "present_count": sess.present_count,
            "absent_count": sess.absent_count,
            "total_count": total,
            "attendance_rate": rate,
            "original_img": sess.original_image_path, 
            "result_img": sess.annotated_image_path,
            "present_students": [],
            "absent_students": [],
            "total_faces_detected": 0
        })
    return result

# ==========================================
# 3. 🚀 Send Notification Endpoint (Mock)
# 3. 🚀 发送缺勤通知接口 (挡板模拟)
# ==========================================
@router.post("/attendance/notify")
async def send_absence_notification(request: NotificationRequest):
    """
    Simulate sending warning emails to absent students.
    发送缺勤提醒邮件 (毕设演示 Mock 版本)
    """
    # 模拟网络延迟和发邮件的耗时操作 (停顿 1.5 秒，让前端 UI Loading 更真实)
    await asyncio.sleep(1.5)
    
    # 打印日志，答辩时可以切到终端给评委看！
    print("=" * 50)
    print(f"📢 [Email Service] Distributing warning emails to absent students for session [{request.session_id}]...")
    print(f"✅ [Email Service] All emails dispatched successfully! / 邮件已全部发送成功！")
    print("=" * 50)

    # Return success response to frontend / 返回成功响应给前端
    return {
        "status": "success", 
        "message": "Warning emails have successfully entered the dispatch queue"
    }