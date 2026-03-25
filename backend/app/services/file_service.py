# backend/app/services/file_service.py
import os
import shutil
import base64
import uuid
from datetime import datetime
from fastapi import UploadFile

# Define base paths
# 定义基础路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")
HISTORY_DIR = os.path.join(STATIC_DIR, "history")
AVATAR_DIR = os.path.join(STATIC_DIR, "avatars")

# Automatically create directories if they don't exist
# 自动创建目录
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

class FileService:
    
    @staticmethod
    async def save_upload_file(file: UploadFile, sub_dir: str = "history") -> str:
        """
        Save the original uploaded file.
        保存上传的原始文件。
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 🚀 Extract file extension safely
        # 🚀 安全地提取文件扩展名 (例如 .jpg, .png)
        _, ext = os.path.splitext(file.filename)
        if not ext:
            ext = ".jpg" # Default fallback / 默认回退
            
        unique_id = uuid.uuid4().hex[:8]
        
        # Safe filename format: 20240501_123030_org_a8f9c2d1.jpg
        # 安全文件名格式
        new_filename = f"{timestamp}_org_{unique_id}{ext}"
        
        save_dir = os.path.join(STATIC_DIR, sub_dir)
        os.makedirs(save_dir, exist_ok=True)
            
        file_path = os.path.join(save_dir, new_filename)
        
        await file.seek(0)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return f"/static/{sub_dir}/{new_filename}"

    @staticmethod
    def save_base64_image(b64_str: str, sub_dir: str = "history") -> str:
        """
        Save Base64 string as an image file with collision prevention.
        保存 Base64 字符串为图片文件 (带防冲突机制)。
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Also added UUID for Base64 saving
        # Base64 保存同样引入 UUID 防止一秒内的大并发覆盖
        unique_id = uuid.uuid4().hex[:8]
        
        # 'res' stands for result
        # res 代表 result
        new_filename = f"{timestamp}_res_{unique_id}.jpg" 
        
        save_dir = os.path.join(STATIC_DIR, sub_dir)
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, new_filename)
        
        # Decode and save
        # 解码并保存
        try:
            with open(file_path, "wb") as f:
                f.write(base64.b64decode(b64_str))
            return f"/static/{sub_dir}/{new_filename}"
        except Exception as e:
            print(f"❌ [FileService] Failed to save Base64 image: {e}")
            return ""