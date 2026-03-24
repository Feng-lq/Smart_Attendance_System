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
    def get_encoding_for_registration(image_np: np.ndarray):
        """
        用于学生录入：从 RGB Numpy 数组中提取单张人脸的 128 维特征向量。
        :param image_np: 已经转为 RGB 格式的图像数组
        :return: 128维的 numpy 数组，如果未检测到则返回 None
        """
        # 提取特征
        encodings = face_recognition.face_encodings(image_np)
        
        # 容错处理
        if len(encodings) == 0:
            return None
        if len(encodings) > 1:
            raise ValueError("照片中检测到多张人脸，注册证件照只能包含学生本人。")
            
        # 返回原生的 numpy 数组，完美适配路由层的 encoding.tolist()
        return encodings[0]

    @staticmethod
    def process_recognition(image_np, known_face_encodings, known_students_data, tolerance=0.55):
        """
        核心识别逻辑
        :param image_np: 待识别图片的 numpy 数组 (RGB)
        :param known_face_encodings: 已知人脸特征值列表
        :param known_students_data: 已知学生信息列表 [{'id': 1, 'name': 'xxx'}, ...]
        :param tolerance: 匹配阈值 (此处设定为0.55，比0.6略微严格，减少合照误认率)
        :return: (result_image_np, found_student_ids)
        """
        # 1. 查找人脸位置
        # 🔥 优化1：增加 upsample=2 图像放大参数，大幅提升暗光和后排小人脸的检测成功率
        face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=2)
        
        # 2. 提取特征值
        face_encodings = face_recognition.face_encodings(image_np, face_locations)

        found_student_ids = []

        # 使用 PIL 进行绘图
        pil_image = Image.fromarray(image_np)
        draw = ImageDraw.Draw(pil_image)

        print(f"--- 识别开始: 共检测到 {len(face_locations)} 张人脸 ---")

        # 遍历每一张检测到的脸
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            match_found = False
            
            # 🔥 优化2：安全防护，确保数据库中有录入的数据，防止 numpy 抛出 argmin 异常
            if len(known_face_encodings) > 0:
                # 计算待测人脸与数据库所有人的欧氏距离
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                
                # 找到距离最近（最相似）的人
                best_match_index = np.argmin(face_distances)
                
                # 判断最相似的人，其距离是否在允许的误差阈值内
                if face_distances[best_match_index] <= tolerance:
                    match_found = True
                    student_info = known_students_data[best_match_index]
                    name = student_info["name"] 
                    found_student_ids.append(student_info["id"]) 
                    
                    print(f"✅ 识别成功: {name}")
                    
                    # 画绿框 (已知)
                    draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0), width=3)
                    
                    # 画名字标签
                    draw.rectangle(((left, bottom - 20), (right, bottom)), fill=(0, 255, 0), outline=(0, 255, 0))
                    draw.text((left + 6, bottom - 18), name, fill=(255, 255, 255, 255))
            
            # 🔥 优化3：如果数据库为空，或者没匹配上任何人，统一画红框 (未知)
            if not match_found:
                draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0), width=3)

        # 转回 numpy 数组 (RGB)
        result_image_np = np.array(pil_image)
        return result_image_np, found_student_ids