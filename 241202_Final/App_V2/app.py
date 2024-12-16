# app.py
from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
from deepface import DeepFace
import base64
import os
import json
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# 配置上传文件的保存路径
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# 可用的分析方案配置
AVAILABLE_SOLUTIONS = {
    'DeepFace': {
        'id': 'deepface',
        'description': 'DeepFace是一个流行的开源人脸分析解决方案，基于深度学习技术。优点是易于使用、功能全面，支持多种预训练模型。适合一般用途和原型开发。速度适中，准确率较好。',
        'package': 'deepface',
        'features': ['年龄预测', '性别识别', '情绪分析', '种族识别'],
        'model_info': 'VGG-Face/OpenCV backend'
    },
    'Face++': {
        'id': 'facepp',
        'description': 'Face++是旷视科技开发的商业级人脸分析API。具有高精度的人脸检测和属性分析能力，服务稳定，适合商业应用。支持更细致的人脸特征分析，包括年龄、性别、情绪等。',
        'package': 'facepplib',
        'features': ['年龄预测', '性别识别', '情绪分析', '颜值打分', '美学分析'],
        'model_info': 'Commercial API/Dense CNN'
    },
    'Dlib': {
        'id': 'dlib',
        'description': 'Dlib是一个包含机器学习算法的C++工具包，其人脸分析模块以准确的人脸关键点检测而闻名。处理速度快，资源占用少，适合嵌入式系统和实时应用。',
        'package': 'dlib',
        'features': ['人脸检测', '关键点定位', '人脸对齐'],
        'model_info': 'HOG/CNN detector'
    },
    'InsightFace': {
        'id': 'insightface',
        'description': 'InsightFace是基于MXNet的开源2D&3D人脸分析工具包，在人脸识别领域享有盛誉。采用SOTA的算法，具有很高的准确率。适合要求高精度的专业应用。',
        'package': 'insightface',
        'features': ['人脸检测', '人脸识别', '关键点检测', '属性分析'],
        'model_info': 'ArcFace/RetinaFace'
    },
    'MediaPipe': {
        'id': 'mediapipe',
        'description': 'MediaPipe是Google开发的跨平台机器学习解决方案。其人脸分析模块轻量级、实时性好，适合移动端和Web应用。支持3D人脸网格和面部表情分析。',
        'package': 'mediapipe',
        'features': ['人脸检测', '3D网格重建', '表情分析'],
        'model_info': 'BlazeFace/TFLite'
    }
}

# 情绪和种族翻译字典
EMOTION_TRANSLATIONS = {
    "neutral": "中性",
    "happy": "高兴",
    "sad": "悲伤",
    "angry": "生气",
    "fear": "恐惧",
    "disgust": "厌恶",
    "surprise": "惊讶"
}

RACE_TRANSLATIONS = {
    "asian": "亚洲人",
    "white": "白人",
    "black": "黑人",
    "middle eastern": "中东人",
    "latino hispanic": "拉丁裔",
    "indian": "印度人"
}

@app.route('/')
def index():
    return render_template('index.html', solutions=AVAILABLE_SOLUTIONS)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 获取上传的文件和选项
        file = request.files.get('image')
        if not file:
            raise ValueError("未上传图片")

        # 获取分析方案和检测选项
        selected_solution = request.form.get('solution', 'deepface')
        detection_options = json.loads(request.form.get('detection_options', '{}'))

        # 保存上传的文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = f"original_{timestamp}.jpg"
        result_filename = f"result_{timestamp}.jpg"
        csv_filename = f"analysis_{timestamp}.csv"

        file_path = os.path.join(UPLOAD_FOLDER, original_filename)
        file.save(file_path)

        # 读取图像并转换颜色空间
        frame = cv2.imread(file_path)
        if frame is None:
            raise ValueError("无法读取图片")
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 获取启用的检测选项
        actions = []
        if detection_options.get('age', False):
            actions.append('age')
        if detection_options.get('gender', False):
            actions.append('gender')
        if detection_options.get('emotion', False):
            actions.append('emotion')
        if detection_options.get('race', False):
            actions.append('race')

        if not actions:
            raise ValueError('请至少选择一个检测选项')

        # 获取当前选择的方案配置
        solution_config = next(
            (solution for solution in AVAILABLE_SOLUTIONS.values() if solution['id'] == selected_solution),
            None
        )

        if not solution_config:
            raise ValueError('无效的方案选择')

        # 使用选定的方案进行分析
        if solution_config['package'] == 'deepface':
            analysis = DeepFace.analyze(
                img_path=rgb_frame,
                actions=actions,
                enforce_detection=False,
                detector_backend='opencv'
            )
        else:
            raise ValueError(f"暂不支持 {solution_config['package']} 方案")

        if not isinstance(analysis, list):
            analysis = [analysis]

        # 处理结果并绘制标注
        results = []
        for idx, face in enumerate(analysis):
            region = face.get('region', {})
            x, y, w, h = region.get('x', 0), region.get('y', 0), region.get('w', 0), region.get('h', 0)

            # 性别判断决定框的颜色
            gender_dict = face.get('gender', {})
            male_prob = gender_dict.get('Man', 0)
            female_prob = gender_dict.get('Woman', 0)

            color = (255, 0, 0) if abs(male_prob - female_prob) <= 20 else (0, 255, 0)

            # 绘制人脸框和序号
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"#{idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 整理结果数据
            result = {
                'id': idx + 1,
                'gender': "未知" if abs(male_prob - female_prob) <= 20 else ("男性" if male_prob > female_prob else "女性"),
                'age': face.get('age', '未知'),
                'emotion': EMOTION_TRANSLATIONS.get(face.get('dominant_emotion', '').lower(), '未知'),
                'race': RACE_TRANSLATIONS.get(face.get('dominant_race', '').lower(), '未知')
            }
            results.append(result)

        # 保存结果图片
        result_path = os.path.join(RESULT_FOLDER, result_filename)
        cv2.imwrite(result_path, frame)

        # 保存分析结果到CSV
        df = pd.DataFrame(results)
        csv_path = os.path.join(RESULT_FOLDER, csv_filename)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        return jsonify({
            'status': 'success',
            'results': results,
            'result_image': f'/static/results/{result_filename}',
            'csv_file': f'/static/results/{csv_filename}'
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(
        os.path.join(RESULT_FOLDER, filename),
        as_attachment=True
    )

if __name__ == '__main__':
    app.run(debug=True)