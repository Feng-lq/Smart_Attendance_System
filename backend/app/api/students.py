# backend/app/api/students.py
import json
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.models import sql_models, database
from app import schemas
from app.api import deps

# Import three core services
# 引入三大服务
from app.services.auth_service import AuthService
from app.services.file_service import FileService
from app.services.face_service import FaceService

router = APIRouter(tags=["Students"])

# 1. Get student list
# 1. 获取学生列表
@router.get("/students", response_model=list[schemas.Student])
def get_students(class_id: int = None, db: Session = Depends(database.get_db)):
    query = db.query(sql_models.Student)
    if class_id:
        query = query.filter(sql_models.Student.class_id == class_id)
    return query.all()

# 2. Create student (Core Refactoring)
# 2. 创建学生 (核心重构)
@router.post("/students")
async def create_student(
    name: str = Form(...),
    student_id: str = Form(...),
    email: str = Form(None), # Allow null / 允许为空
    class_id: int = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # A. Pre-check: Verify if student ID already exists
    # A. 预检查：学号是否已存在
    existing_student = db.query(sql_models.Student).filter(sql_models.Student.student_id == student_id).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student ID already exists")

    # B. Process face image (using FaceService)
    # B. 处理人脸 (使用 FaceService)
    try:
        # Load image
        # 加载图片
        image_np = await FaceService.load_image_from_file(file)
        
        # Extract features (Call the method added in step 1)
        # 提取特征 (调用我们在第一步新增的方法)
        encoding = FaceService.get_encoding_for_registration(image_np)
        
        if encoding is None:
            raise HTTPException(status_code=400, detail="No face detected. Please upload a clear frontal portrait photo without a hat")
            
        # Serialize feature vector
        # 序列化特征值
        encoding_json = json.dumps(encoding.tolist())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face processing failed: {str(e)}")

    # C. Save file (using FileService)
    # Store student photos separately in the 'avatars' folder for better organization
    # C. 保存文件 (使用 FileService) - 将学生照片单独存放在 avatars 文件夹，更规范
    try:
        photo_path = await FileService.save_upload_file(file, sub_dir="avatars")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File saving failed: {str(e)}")

    # D. Password encryption (using AuthService)
    # D. 密码加密 (使用 AuthService)
    default_pwd = "123456"
    hashed_pwd = AuthService.hash_password(default_pwd)

    # E. Write to database
    # E. 写入数据库
    new_student = sql_models.Student(
        name=name,
        student_id=student_id,
        class_id=class_id,
        email=email,
        hashed_password=hashed_pwd,     # Store cipher text / 存密文
        photo_path=photo_path,          # Store relative path / 存相对路径 /static/avatars/xxx.jpg
        face_encoding=encoding_json     # Store feature vector / 存特征向量
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {"message": "Student registered successfully", "student_id": new_student.id}

# 3. Delete student
# 3. 删除学生
@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    student = db.query(sql_models.Student).filter(sql_models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    return {"message": "Deleted successfully"}

# 🔥 NEW: Get attendance records for the currently logged-in student
# 🔥 新增：获取当前登录学生的考勤记录
@router.get("/students/me/attendance")
def get_my_attendance(
    current_student: sql_models.Student = Depends(deps.get_current_student),
    db: Session = Depends(database.get_db)
):
    """
    Student Portal API: Query my own attendance history
    学生端接口：查询我自己的考勤历史
    """
    # Query all attendance records for this student (Record table) and join Session table to get time, images, etc.
    # 查询该学生的所有考勤记录 (Record 表)，并关联 Session 表获取时间、图片等信息
    records = db.query(sql_models.AttendanceRecord)\
        .join(sql_models.AttendanceSession)\
        .filter(sql_models.AttendanceRecord.student_id == current_student.id)\
        .order_by(sql_models.AttendanceSession.created_at.desc())\
        .all()
    
    result = []
    for r in records:
        # Get corresponding attendance session info
        # 拿到对应的考勤场次信息
        session_info = r.session
        
        result.append({
            "session_id": session_info.id,
            "class_name": session_info.clazz.name if session_info.clazz else "Deleted Course",
            "created_at": session_info.created_at.strftime("%Y-%m-%d %H:%M"),
            "status": r.status, # present or absent
            "result_img": session_info.annotated_image_path # Result annotated image
        })
    
    return result

# =======================
# 🔥 NEW: Student inquiry API (by student ID)
# =======================
@router.get("/student/portal/{student_id}")
def get_student_attendance_detail(student_id: str, db: Session = Depends(database.get_db)):
    # 1. Find the student
    # 1. 找学生
    student = db.query(sql_models.Student).filter(sql_models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student with this ID not found")
    
    # 2. Find all attendance records for this student
    # 2. 找这个学生的所有考勤记录
    records = db.query(sql_models.AttendanceRecord).filter(sql_models.AttendanceRecord.student_id == student.id).all()
    
    # 3. Calculate statistics
    # 3. 统计数据
    total_sessions = len(records)
    present_count = sum(1 for r in records if r.status == "present")
    absent_count = sum(1 for r in records if r.status == "absent")
    rate = round((present_count / total_sessions) * 100, 1) if total_sessions > 0 else 0.0
    
    # 4. Construct detailed history list
    # 4. 构造详细历史列表
    history_list = []
    for r in records:
        # Query corresponding Session info (to get the timestamp)
        # 查对应的 Session 信息（为了拿时间）
        session = db.query(sql_models.AttendanceSession).filter(sql_models.AttendanceSession.id == r.session_id).first()
        if session:
            history_list.append({
                "session_id": session.id,
                "date": session.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": r.status,
                "evidence_img": session.annotated_image_path 
            })
            
    # Sort by time in descending order
    # 按时间倒序
    history_list.sort(key=lambda x: x["date"], reverse=True)

    return {
        "student_info": {
            "name": student.name,
            "student_id": student.student_id,
            "class_name": student.student_class.name if student.student_class else "Unknown Class",
            "photo_path": student.photo_path
        },
        "stats": {
            "total": total_sessions,
            "present": present_count,
            "absent": absent_count,
            "rate": rate
        },
        "history": history_list
    }