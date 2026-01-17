# backend/app/services/face_engine.py
import cv2
import face_recognition
import numpy as np
import io
import base64
from PIL import Image

class FaceEngine:
    @staticmethod
    def process_and_annotate(rgb_image, face_locations, face_encodings, known_encodings, known_student_data, tolerance=0.6):
        """
        核心算法：比对人脸并在原图上绘制标注框
        :param tolerance: 容差值，默认为 0.6。越低越严格（容易Unknown），越高越宽松（容易认错人）。
        """
        present_students = []
        matched_student_ids = set()

        # 转换为 BGR 用于 OpenCV 绘图
        annotated_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

        print(f"--- 开始识别 ---")
        print(f"当前已知底库人数: {len(known_encodings)}")
        print(f"画面中检测到人脸数: {len(face_encodings)}")

        for idx, ((top, right, bottom, left), face_encoding) in enumerate(zip(face_locations, face_encodings)):
            name = "Unknown"
            color = (0, 0, 255)  # 默认红色 (BGR) - 未识别

            if known_encodings:
                # 1. 计算与底库中所有人脸的欧氏距离 (越小越像)
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                
                # 2. 找到最相似的那个人的索引
                best_match_index = np.argmin(face_distances)
                min_distance = face_distances[best_match_index]

                # Debug: 打印每张脸的匹配详情
                print(f"[人脸 {idx}] 最小距离: {min_distance:.4f} (阈值: {tolerance}) -> 对应学生: {known_student_data[best_match_index]['name']}")

                # 3. 只有当最小距离小于阈值时，才认为是匹配成功
                if min_distance <= tolerance:
                    student_info = known_student_data[best_match_index]
                    
                    # 防止同一张照片里同一个人被识别两次（去重）
                    if student_info["id"] not in matched_student_ids:
                        name = student_info["name"]
                        color = (0, 255, 0)  # 绿色 - 识别成功
                        matched_student_ids.add(student_info["id"])
                        present_students.append(student_info)
                        print(f"   >>> 判定为匹配成功！")
                    else:
                        print(f"   >>> 匹配成功但已在列表中 (去重)")
                else:
                    print(f"   >>> 距离过大，判定为 Unknown")

            # 绘制矩形框
            cv2.rectangle(annotated_image, (left, top), (right, bottom), color, 2)
            
            # 绘制名字背景条
            cv2.rectangle(annotated_image, (left, bottom - 25), (right, bottom), color, cv2.FILLED)
            
            # 绘制名字 (只支持英文，中文会乱码，如需中文需要用 PIL 绘制)
            cv2.putText(annotated_image, name, (left + 6, bottom - 6), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

        # 结果图转 Base64
        final_rgb = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(final_rgb)
        buff = io.BytesIO()
        pil_img.save(buff, format="JPEG", quality=80)
        encoded_base64 = base64.b64encode(buff.getvalue()).decode('utf-8')

        return encoded_base64, present_students, matched_student_ids