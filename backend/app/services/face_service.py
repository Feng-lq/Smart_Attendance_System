# backend/app/services/face_service.py
import face_recognition
import cv2
import numpy as np
import io
import json
from fastapi import UploadFile
from PIL import Image, ImageDraw, ImageFont

class FaceService:
    
    @staticmethod
    async def load_image_from_file(file: UploadFile) -> np.ndarray:
        """
        Read UploadFile and convert to numpy array (RGB format)
        读取 UploadFile 并转换为 numpy 数组 (RGB格式)
        """
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to RGB
        # 转换为 RGB
        img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        return img_rgb

    @staticmethod
    def get_encoding_for_registration(image_np: np.ndarray):
        """
        Used for student registration: Extract a 128D feature vector of a single face.
        用于学生录入：提取单张人脸的 128 维特征向量。
        """
        encodings = face_recognition.face_encodings(image_np)
        
        if len(encodings) == 0:
            return None
        if len(encodings) > 1:
            raise ValueError("Multiple faces detected. The registration photo must only contain the student.")
            
        return encodings[0]

    @staticmethod
    def process_recognition(image_np, known_face_encodings, known_students_data, tolerance=0.55):
        """
        Core recognition logic with Dynamic UI Scaling
        带有动态 UI 缩放的核心识别逻辑
        """
        face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=2)
        face_encodings = face_recognition.face_encodings(image_np, face_locations)

        found_student_ids = []

        pil_image = Image.fromarray(image_np)
        draw = ImageDraw.Draw(pil_image)
        
        # 🚀 [Optimized] Dynamic UI Scaling Logic
        # 🚀 [优化提升] 动态分辨率缩放逻辑
        img_width, img_height = pil_image.size
        
        # Calculate dynamic line width (e.g., 3px for 1000px width, dynamically thicker for 4K images)
        # 根据图像宽度动态计算线条粗细 (比如 1000px 宽度对应 3px 粗细，4K大图会自动变粗)
        dynamic_line_width = max(2, int(img_width * 0.003)) 
        
        # Calculate dynamic label box height
        # 动态计算标签背景框的高度
        label_h = max(20, int(img_height * 0.025))

        print(f"--- Recognition started: {len(face_locations)} face(s) detected ---")

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            match_found = False
            
            if len(known_face_encodings) > 0:
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                
                if face_distances[best_match_index] <= tolerance:
                    match_found = True
                    student_info = known_students_data[best_match_index]
                    name = student_info["name"] 
                    found_student_ids.append(student_info["id"]) 
                    
                    print(f"✅ Recognition successful: {name}")
                    
                    # Draw dynamically scaled green box (Known)
                    # 绘制动态缩放的绿框 (已知)
                    draw.rectangle(
                        ((left, top), (right, bottom)), 
                        outline=(0, 255, 0), 
                        width=dynamic_line_width
                    )
                    
                    # Draw dynamically scaled name label
                    # 绘制动态缩放的名字标签板
                    draw.rectangle(
                        ((left, bottom - label_h), (right, bottom)), 
                        fill=(0, 255, 0), 
                        outline=(0, 255, 0)
                    )
                    draw.text((left + 6, bottom - label_h + 2), name, fill=(255, 255, 255, 255))
            
            if not match_found:
                # Draw dynamically scaled red box (Unknown)
                # 绘制动态缩放的红框 (未知)
                draw.rectangle(
                    ((left, top), (right, bottom)), 
                    outline=(255, 0, 0), 
                    width=dynamic_line_width
                )

        result_image_np = np.array(pil_image)
        return result_image_np, found_student_ids