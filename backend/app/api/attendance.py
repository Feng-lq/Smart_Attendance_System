# backend/app/api/attendance.py
import json
import uuid
import cv2
import os
import numpy as np
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import database, sql_models
from app import schemas

# 引入核心服务
from app.services.face_service import FaceService
from app.services.file_service import FileService

router = APIRouter(tags=["Attendance"])

# ===========================
# 1. 核心考勤识别接口
# ===========================
@router.post("/attendance/recognize", response_model=schemas.AttendanceSessionOut)
async def recognize_attendance(
    class_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # A. 验证班级
    clazz = db.query(sql_models.Class).filter(sql_models.Class.id == class_id).first()
    if not clazz:
        raise HTTPException(status_code=404, detail="班级不存在")

    # B. 准备已知人脸数据
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
        raise HTTPException(status_code=400, detail="该班级没有录入人脸数据")

    # C. 保存原始上传图片
    try:
        original_path = await FileService.save_upload_file(file, sub_dir="history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存图片失败: {str(e)}")

    # 重置文件指针
    await file.seek(0)

    # D. 调用 FaceService 进行识别
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
        raise HTTPException(status_code=500, detail=f"识别算法出错: {str(e)}")

    # E. 保存结果图片
    filename = os.path.basename(original_path)
    result_filename = f"result_{filename}"
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    save_dir = os.path.join(base_dir, "static", "history")
    os.makedirs(save_dir, exist_ok=True)
    
    result_path_disk = os.path.join(save_dir, result_filename)
    
    # 写入文件 (RGB -> BGR)
    result_img_bgr = cv2.cvtColor(result_img_np, cv2.COLOR_RGB2BGR)
    cv2.imwrite(result_path_disk, result_img_bgr)

    # URL 路径
    result_path_db = f"/static/history/{result_filename}"

    # F. 写入数据库
    present_count = len(set(found_ids))
    total_count = len(students)
    absent_count = total_count - present_count
    
    # 计算出勤率 (仅用于显示，不存数据库)
    attendance_rate = round((present_count / total_count) * 100, 2) if total_count > 0 else 0.0
    
    # 生成 UUID (因为数据库 id 是 String 类型)
    session_id = str(uuid.uuid4())
    
    new_session = sql_models.AttendanceSession(
        id=session_id,  # 🔥 必须手动生成
        class_id=class_id,
        created_at=datetime.now(),
        original_image_path=original_path, 
        annotated_image_path=result_path_db,
        present_count=present_count,
        absent_count=absent_count
        # ❌ 已删除 attendance_rate=... 因为数据库表里没有
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # 写入明细记录
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

    # G. 构造返回值
    return {
        "id": str(new_session.id),
        "class_name": clazz.name,
        "created_at": new_session.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "present_count": present_count,
        "absent_count": absent_count,
        "total_count": total_count,
        "attendance_rate": attendance_rate, # 这是算出来给前端看的
        "original_img": original_path,
        "result_img": result_path_db, 
        "present_students": present_students_list, 
        "absent_students": absent_students_list,   
        "total_faces_detected": len(found_ids) 
    }

# ===========================
# 2. 获取考勤历史接口
# ===========================
@router.get("/attendance/history", response_model=list[schemas.AttendanceSessionOut])
def get_attendance_history(db: Session = Depends(database.get_db)):
    sessions = db.query(sql_models.AttendanceSession).order_by(sql_models.AttendanceSession.created_at.desc()).all()
    
    result = []
    for sess in sessions:
        clazz = db.query(sql_models.Class).filter(sql_models.Class.id == sess.class_id).first()
        
        total = sess.present_count + sess.absent_count
        # 现场计算出勤率
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