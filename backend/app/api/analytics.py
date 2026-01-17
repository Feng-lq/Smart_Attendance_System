# backend/app/api/analytics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models import database, sql_models
from typing import List

router = APIRouter(tags=["Analytics"])

# 1. 获取班级出勤率趋势 (折线图数据)
@router.get("/analytics/class_trend/{class_id}")
def get_class_trend(class_id: int, db: Session = Depends(database.get_db)):
    # 查询该班级的所有考勤批次，按时间正序排列
    sessions = db.query(sql_models.AttendanceSession)\
        .filter(sql_models.AttendanceSession.class_id == class_id)\
        .order_by(sql_models.AttendanceSession.created_at.asc())\
        .all()
    
    trend_data = []
    for s in sessions:
        total = s.present_count + s.absent_count
        rate = round((s.present_count / total * 100), 1) if total > 0 else 0
        
        trend_data.append({
            "date": s.created_at.strftime("%Y-%m-%d %H:%M"), # X轴: 时间
            "rate": rate,                                     # Y轴: 出勤率
            "total": total,
            "present": s.present_count
        })
    
    return trend_data

# 2. 获取缺勤“黑名单”排行榜 (谁缺勤最多?)
@router.get("/analytics/absent_ranking/{class_id}")
def get_absent_ranking(class_id: int, db: Session = Depends(database.get_db)):
    # 这是一个复杂的聚合查询：
    # 1. 在 attendance_records 表中筛选 status='absent'
    # 2. 关联 student 表 (为了拿名字)
    # 3. 筛选特定 class_id
    # 4. 分组并计数
    # 5. 按缺勤次数倒序排
    
    results = db.query(
        sql_models.Student.name,
        sql_models.Student.student_id,
        func.count(sql_models.AttendanceRecord.id).label("absent_count")
    ).join(sql_models.AttendanceRecord, sql_models.Student.id == sql_models.AttendanceRecord.student_id)\
     .filter(sql_models.Student.class_id == class_id)\
     .filter(sql_models.AttendanceRecord.status == "absent")\
     .group_by(sql_models.Student.id)\
     .order_by(desc("absent_count"))\
     .limit(10)\
     .all()
    
    # 格式化返回
    ranking = []
    for name, sid, count in results:
        ranking.append({
            "name": name,
            "student_id": sid,
            "count": count
        })
        
    return ranking