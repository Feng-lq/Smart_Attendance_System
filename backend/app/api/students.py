# backend/app/api/students.py
import json
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.models import sql_models, database
from app import schemas
from app.api import deps

# 引入三大服务
from app.services.auth_service import AuthService
from app.services.file_service import FileService
from app.services.face_service import FaceService

router = APIRouter(tags=["Students"])

# 1. 获取学生列表
@router.get("/students", response_model=list[schemas.Student])
def get_students(class_id: int = None, db: Session = Depends(database.get_db)):
    query = db.query(sql_models.Student)
    if class_id:
        query = query.filter(sql_models.Student.class_id == class_id)
    return query.all()

# 2. 创建学生 (核心重构)
@router.post("/students")
async def create_student(
    name: str = Form(...),
    student_id: str = Form(...),
    email: str = Form(None), # 允许为空
    class_id: int = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # A. 预检查：学号是否已存在
    existing_student = db.query(sql_models.Student).filter(sql_models.Student.student_id == student_id).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="该学号已存在")

    # B. 处理人脸 (使用 FaceService)
    try:
        # 加载图片
        image_np = await FaceService.load_image_from_file(file)
        
        # 提取特征 (调用我们在第一步新增的方法)
        encoding = FaceService.get_encoding_for_registration(image_np)
        
        if encoding is None:
            raise HTTPException(status_code=400, detail="未检测到人脸，请上传清晰的正面免冠照")
            
        # 序列化特征值
        encoding_json = json.dumps(encoding.tolist())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"人脸处理失败: {str(e)}")

    # C. 保存文件 (使用 FileService)
    # 将学生照片单独存放在 avatars 文件夹，更规范
    try:
        photo_path = await FileService.save_upload_file(file, sub_dir="avatars")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

    # D. 密码加密 (使用 AuthService)
    default_pwd = "123456"
    hashed_pwd = AuthService.hash_password(default_pwd)

    # E. 写入数据库
    new_student = sql_models.Student(
        name=name,
        student_id=student_id,
        class_id=class_id,
        email=email,
        hashed_password=hashed_pwd,     # 存密文
        photo_path=photo_path,          # 存相对路径 /static/avatars/xxx.jpg
        face_encoding=encoding_json     # 存特征向量
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {"message": "学生录入成功", "student_id": new_student.id}

# 3. 删除学生 (顺手补全)
@router.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(database.get_db)):
    student = db.query(sql_models.Student).filter(sql_models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    
    db.delete(student)
    db.commit()
    return {"message": "删除成功"}

# 🔥 新增：获取当前登录学生的考勤记录
@router.get("/students/me/attendance")
def get_my_attendance(
    current_student: sql_models.Student = Depends(deps.get_current_student),
    db: Session = Depends(database.get_db)
):
    """
    学生端接口：查询我自己的考勤历史
    """
    # 查询该学生的所有考勤记录 (Record 表)，并关联 Session 表获取时间、图片等信息
    records = db.query(sql_models.AttendanceRecord)\
        .join(sql_models.AttendanceSession)\
        .filter(sql_models.AttendanceRecord.student_id == current_student.id)\
        .order_by(sql_models.AttendanceSession.created_at.desc())\
        .all()
    
    result = []
    for r in records:
        # 拿到对应的考勤场次信息
        session_info = r.session
        
        result.append({
            "session_id": session_info.id,
            "class_name": session_info.clazz.name if session_info.clazz else "已删除课程",
            "created_at": session_info.created_at.strftime("%Y-%m-%d %H:%M"),
            "status": r.status, # present 或 absent
            "result_img": session_info.annotated_image_path # 结果图
        })
    
    return result

# =======================
# 🔥 新增：学生端查询接口
# =======================
@router.get("/student/portal/{student_id}")
def get_student_attendance_detail(student_id: str, db: Session = Depends(database.get_db)):
    # 1. 找学生
    student = db.query(sql_models.Student).filter(sql_models.Student.student_id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="未找到该学号的学生")
    
    # 2. 找这个学生的所有考勤记录
    records = db.query(sql_models.AttendanceRecord).filter(sql_models.AttendanceRecord.student_id == student.id).all()
    
    # 3. 统计数据
    total_sessions = len(records)
    present_count = sum(1 for r in records if r.status == "present")
    absent_count = sum(1 for r in records if r.status == "absent")
    rate = round((present_count / total_sessions) * 100, 1) if total_sessions > 0 else 0.0
    
    # 4. 构造详细历史列表
    history_list = []
    for r in records:
        # 查对应的 Session 信息（为了拿时间）
        session = db.query(sql_models.AttendanceSession).filter(sql_models.AttendanceSession.id == r.session_id).first()
        if session:
            history_list.append({
                "session_id": session.id,
                "date": session.created_at.strftime("%Y-%m-%d %H:%M"),
                "status": r.status,
                # 如果你想让学生看到自己当时的识别图（可选）
                # "evidence_img": session.annotated_image_path 
            })
            
    # 按时间倒序
    history_list.sort(key=lambda x: x["date"], reverse=True)

    return {
        "student_info": {
            "name": student.name,
            "student_id": student.student_id,
            "class_name": student.student_class.name if student.student_class else "未知班级",
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