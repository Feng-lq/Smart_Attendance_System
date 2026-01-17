import os
import json
import shutil
import face_recognition
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.models import sql_models, database  # 导入模型和数据库配置

# 1. 创建路由对象
router = APIRouter(tags=["Students"])

# 2. 获取学生列表（支持按班级筛选）
@router.get("/students")
def get_students(class_id: int = None, db: Session = Depends(database.get_db)):
    query = db.query(sql_models.Student)
    if class_id:
        query = query.filter(sql_models.Student.class_id == class_id)
    return query.all()

# 3. 创建学生（含人脸检测与特征存储）
@router.post("/students")
async def create_student(
    name: str = Form(...),
    student_id: str = Form(...),
    email: str = Form(...),
    class_id: int = Form(...), 
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # 确保保存路径与 main.py 挂载的 static 一致
    file_location = f"static/uploads/{student_id}_{file.filename}"
    
    # 保存图片文件到本地
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 提取人脸特征值
        image = face_recognition.load_image_file(file_location)
        encodings = face_recognition.face_encodings(image)
        
        if not encodings:
            # 如果没检测到人脸，删除刚上传的文件并报错
            if os.path.exists(file_location):
                os.remove(file_location)
            raise HTTPException(status_code=400, detail="未检测到人脸，请重新上传清晰的正面照")
        
        # 将特征向量转换为 JSON 字符串存入 PGSQL
        encoding_json = json.dumps(encodings[0].tolist())

        # 写入数据库
        new_student = sql_models.Student(
            name=name,
            student_id=student_id,
            email=email,
            class_id=class_id,
            photo_path=file_location,
            face_encoding=encoding_json
        )
        db.add(new_student)
        db.commit()
        return {"message": "学生信息及人脸特征已成功录入"}
        
    except Exception as e:
        # 发生任何错误时清理上传的文件
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"录入失败: {str(e)}")