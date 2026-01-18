# backend/app/services/file_service.py
import os
import shutil
import base64
from datetime import datetime
from fastapi import UploadFile

# 定义基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")
HISTORY_DIR = os.path.join(STATIC_DIR, "history")
AVATAR_DIR = os.path.join(STATIC_DIR, "avatars")

# 自动创建目录
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

class FileService:
    @staticmethod
    async def save_upload_file(file: UploadFile, sub_dir: str = "history") -> str:
        """保存上传的原始文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_filename = file.filename.replace(" ", "_")
        # 加上 random 后缀防止同一秒并发上传重名
        new_filename = f"{timestamp}_org_{clean_filename}"
        
        save_dir = os.path.join(STATIC_DIR, sub_dir)
        os.makedirs(save_dir, exist_ok=True)
            
        file_path = os.path.join(save_dir, new_filename)
        
        # 指针重置 (关键！因为 Controller 可能读取过它)
        await file.seek(0)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return f"/static/{sub_dir}/{new_filename}"

    @staticmethod
    def save_base64_image(b64_str: str, sub_dir: str = "history") -> str:
        """🔥 新增：保存 Base64 字符串为图片文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}_res.jpg" # res 代表 result
        
        save_dir = os.path.join(STATIC_DIR, sub_dir)
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, new_filename)
        
        # 解码并保存
        try:
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(b64_str))
            return f"/static/{sub_dir}/{new_filename}"
        except Exception as e:
            print(f"❌ 保存 Base64 图片失败: {e}")
            return ""