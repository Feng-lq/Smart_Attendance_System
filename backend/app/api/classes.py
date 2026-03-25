from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import sql_models, database  # Ensure correct import path / 确保导入路径正确

# Create router object, add tags for better classification in Swagger UI
# 创建路由对象，添加 tags 方便在 Swagger UI 中分类查看
router = APIRouter(tags=["Classes"])

# 1. Get class list (with student count statistics)
# 1. 获取班级列表（带学生人数统计）
@router.get("/classes")
def get_classes(db: Session = Depends(database.get_db)):
    # Use outerjoin to count students, ensuring classes without students show 0
    # 使用 outerjoin 统计人数，确保没有学生的班级也能显示 0
    classes_with_count = db.query(
        sql_models.Class.id,
        sql_models.Class.name,
        func.count(sql_models.Student.id).label("student_count")
    ).outerjoin(sql_models.Student)\
     .group_by(sql_models.Class.id)\
     .order_by(sql_models.Class.id.asc())\
     .all()
    
    return [
        {"id": c.id, "name": c.name, "student_count": c.student_count} 
        for c in classes_with_count
    ]

# 2. Create a new class
# 2. 新建班级
@router.post("/classes")
async def create_class(name: str = Form(...), db: Session = Depends(database.get_db)):
    # Check for duplicate class names
    # 检查重名
    existing = db.query(sql_models.Class).filter(sql_models.Class.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Class name already exists")
    
    new_class = sql_models.Class(name=name)
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class

# 3. Delete a class
# 3. 删除班级
@router.delete("/classes/{class_id}")
def delete_class(class_id: int, db: Session = Depends(database.get_db)):
    # Security check: Do not allow deletion if the class still has students
    # 安全检查：班级有学生时不允许删除
    has_students = db.query(sql_models.Student).filter(sql_models.Student.class_id == class_id).first()
    if has_students:
        raise HTTPException(status_code=400, detail="Cannot delete class: there are still students enrolled. Please remove them first.")
    
    db_class = db.query(sql_models.Class).filter(sql_models.Class.id == class_id).first()
    if not db_class:
        raise HTTPException(status_code=404, detail="Class not found")
    
    db.delete(db_class)
    db.commit()
    return {"message": "Class deleted successfully"}