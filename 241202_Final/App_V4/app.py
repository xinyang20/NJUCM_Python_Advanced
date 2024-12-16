# app.py
from flask import Flask, render_template, request, jsonify, send_file
import cv2
from deepface import DeepFace
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
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # 获取上传的文件和选项
        file = request.files.get('image')
        if not file:
            raise ValueError("未上传图片")

        # 获取检测选项
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

        # 使用DeepFace进行分析
        analysis = DeepFace.analyze(
            img_path=rgb_frame,
            actions=actions,
            enforce_detection=False,
            detector_backend='opencv'
        )

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

            color = (0, 0, 255) if abs(male_prob - female_prob) <= 20 else (0, 255, 0)

            # 绘制人脸框和序号
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"#{idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 整理结果数据
            result = {
                'id': idx + 1,
                'gender': f"未知(男：{male_prob:.2f},女：{female_prob:.2f})" if abs(male_prob - female_prob) <= 20 else (
                    "男性" if male_prob > female_prob else "女性"),
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