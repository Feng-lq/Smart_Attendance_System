# backend/app/api/attendance.py
import os
import io
import json
import uuid
import base64
import face_recognition
import numpy as np
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session

# 导入数据库依赖和模型
from app.models import database, sql_models
# 导入已经迁移到 services 层的核心算法
from app.services.face_engine import FaceEngine 

# 1. 定义路由对象，必须叫 router 以便 main.py 引用
router = APIRouter(tags=["Attendance"])

# 定义图片保存目录
HISTORY_DIR = "static/history"
os.makedirs(HISTORY_DIR, exist_ok=True)

@router.post("/attendance/class_photo")
async def process_class_photo(
    class_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db) # 👈 使用 database.py 里的依赖
):
    try:
        # 1. 读取上传的大合照字节流
        image_data = await file.read()
        # 直接加载字节流，face_recognition 会处理为 RGB 格式
        rgb_image = face_recognition.load_image_file(io.BytesIO(image_data))
        
        # 2. 在合照中检测所有人脸位置并提取特征值
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        # 3. 获取该班级在数据库中已录入的学生名单及特征
        students_in_class = db.query(sql_models.Student).filter(sql_models.Student.class_id == class_id).all()
        
        known_encodings = []
        known_student_data = [] # 用于映射识别结果
        
        for s in students_in_class:
            # 性能优化：如果数据库存了 face_encoding (JSON)，直接解析，无需重读照片
            if s.face_encoding and os.path.exists(s.photo_path):
                encoding = np.array(json.loads(s.face_encoding))
                known_encodings.append(encoding)
                known_student_data.append({"id": s.id, "name": s.name, "email": s.email})

        # 4. 调用服务层 FaceEngine 进行比对和 OpenCV 图像标注
        # 返回值解构：Base64标注图, 已到学生列表, 已到学生ID集合
        encoded_img, present_students, matched_ids = FaceEngine.process_and_annotate(
            rgb_image, 
            face_locations, 
            face_encodings, 
            known_encodings, 
            known_student_data
        )

        # 5. 确定缺席学生名单
        absent_students = []
        for s in students_in_class:
            if s.id not in matched_ids:
                absent_students.append({"id": s.id, "name": s.name, "email": s.email})

        # === 保存数据到历史记录 ===
        session_id = str(uuid.uuid4())
        
        # A. 保存图片文件
        # 保存原图
        org_filename = f"{session_id}_org.jpg"
        org_path = f"{HISTORY_DIR}/{org_filename}"
        with open(org_path, "wb") as f:
            f.write(image_data)
            
        # 保存结果图 (Base64 -> File)
        res_filename = f"{session_id}_res.jpg"
        res_path = f"{HISTORY_DIR}/{res_filename}"
        with open(res_path, "wb") as f:
            f.write(base64.b64decode(encoded_img))
            
        # B. 写入数据库 Session
        new_session = sql_models.AttendanceSession(
            id=session_id,
            class_id=class_id,
            created_at=datetime.now(),
            original_image_path=f"/{org_path}",  # 存相对路径供前端访问
            annotated_image_path=f"/{res_path}",
            present_count=len(present_students),
            absent_count=len(absent_students)
        )
        db.add(new_session)
        db.commit()

        # C. 写入数据库 Records
        records = []
        for stu in present_students:
            records.append(sql_models.AttendanceRecord(session_id=session_id, student_id=stu['id'], status="present"))
        for stu in absent_students:
            records.append(sql_models.AttendanceRecord(session_id=session_id, student_id=stu['id'], status="absent"))
        
        db.add_all(records)
        db.commit()

        # 6. 返回最终结果给前端
        return {
            "session_id": str(uuid.uuid4()),
            "present_count": len(present_students),
            "absent_count": len(absent_students),
            "present_students": present_students,
            "absent_students": absent_students,
            "total_faces_detected": len(face_locations),
            "class_total": len(students_in_class),
            "annotated_image_base64": encoded_img
        }

    except Exception as e:
        # 打印详细报错到后端终端
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")
    
@router.get("/attendance/history")
def get_attendance_history(db: Session = Depends(database.get_db)):
    # 按时间倒序查询所有历史
    sessions = db.query(sql_models.AttendanceSession)\
        .order_by(sql_models.AttendanceSession.created_at.desc())\
        .all()
    
    result = []
    for s in sessions:
        # 🚀 重点修改：直接使用数据库字段，无需 len(s.records)，性能提升 10倍
        p_count = s.present_count
        a_count = s.absent_count
        total = p_count + a_count
        
        result.append({
            "id": s.id, # 前端用的 key 是 id 还是 session_id 请确认，建议统一用 id
            "class_name": s.clazz.name if s.clazz else "已删除班级",
            "created_at": s.created_at.strftime("%Y-%m-%d %H:%M"),
            "present_count": p_count,
            "absent_count": a_count, # 前端需要这个字段
            "total_count": total,
            "attendance_rate": round((p_count / total * 100), 1) if total > 0 else 0,
            "original_img": s.original_image_path,
            "result_img": s.annotated_image_path
        })
    return result