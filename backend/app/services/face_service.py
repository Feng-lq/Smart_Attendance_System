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
        读取 UploadFile 并转换为 numpy 数组 (RGB格式)
        """
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # 转换为 RGB (因为 face_recognition 使用 RGB)
        img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        return img_rgb

    @staticmethod
    def get_face_encoding_from_bytes(image_bytes: bytes) -> str | None:
        """从字节流提取特征 (用于录入学生)"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(img_rgb)
            if len(encodings) > 0:
                return json.dumps(encodings[0].tolist())
            return None
        except Exception as e:
            print(f"特征提取出错: {e}")
            return None

    @staticmethod
    def process_recognition(image_np, known_face_encodings, known_students_data, tolerance=0.6):
        """
        核心识别逻辑
        :param image_np: 待识别图片的 numpy 数组 (RGB)
        :param known_face_encodings: 已知人脸特征值列表
        :param known_students_data: 已知学生信息列表 [{'id': 1, 'name': 'xxx'}, ...]
        :return: (result_image_np, found_student_ids)
        """
        # 1. 查找人脸位置
        face_locations = face_recognition.face_locations(image_np)
        # 2. 提取特征值
        face_encodings = face_recognition.face_encodings(image_np, face_locations)

        found_student_ids = []

        # 使用 PIL 进行绘图 (支持中文更好，或者单纯为了画框方便)
        pil_image = Image.fromarray(image_np)
        draw = ImageDraw.Draw(pil_image)

        print(f"--- 识别开始: 检测到 {len(face_locations)} 张人脸 ---")

        # 遍历每一张检测到的脸
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=tolerance)
            name = "Unknown"
            
            # 计算人脸距离 (越小越相似)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            
            # 找到最相似的那个
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                # 🔥 修正：现在获取的是字典，可以安全使用 ["name"] 和 ["id"]
                student_info = known_students_data[best_match_index]
                name = student_info["name"] 
                found_student_ids.append(student_info["id"]) 
                
                print(f"✅ 识别成功: {name}")
                
                # 画绿框 (已知)
                draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0), width=3)
                
                # 画名字标签
                # 如果没有中文字体，暂时用简单的矩形和英文/拼音
                text_len = len(name) * 10
                draw.rectangle(((left, bottom - 20), (right, bottom)), fill=(0, 255, 0), outline=(0, 255, 0))
                draw.text((left + 6, bottom - 18), name, fill=(255, 255, 255, 255))
            else:
                # 画红框 (未知)
                draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0), width=3)

        # 转回 numpy 数组 (RGB)
        result_image_np = np.array(pil_image)
        return result_image_np, found_student_ids