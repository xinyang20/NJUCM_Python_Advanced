import os

from flask import Flask, render_template, jsonify, request
from PIL import Image, ImageDraw
from werkzeug.utils import secure_filename


class Config:
    UPLOAD_FOLDER = 'static/uploads'
    RESULT_FOLDER = 'static/results'
    LOG_FOLDER = 'logs'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 限制
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    MODEL_PATHS = {
        'DeepFace': {
            'id': 'deepface',
            'name': 'DeepFace',
            'description': 'DeepFace是一个流行的开源人脸分析解决方案，基于深度学习技术。',
            'features': ['年龄检测', '性别检测', '情绪检测', '种族检测'],
            'model_info': 'VGG-Face/OpenCV backend'
        },
        'Face++': {
            'id': 'facepp',
            'name': 'Face++',
            'description': 'Face++是旷视科技开发的商业级人脸分析API。',
            'features': ['年龄检测', '性别检测', '情绪检测', '颜值打分'],
            'model_info': 'Commercial API'
        },
    }

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return render_template('index.html', solutions=app.config['MODEL_PATHS'])

@app.route('/get_features/<model_id>', methods=['GET'])
def get_features(model_id):
    try:
        model = next((m for m in app.config['MODEL_PATHS'].values() if m['id'] == model_id), None)
        if model:
            return jsonify({'status': 'success', 'features': model['features']})
        return jsonify({'status': 'error', 'message': '模型未找到'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def allowed_file(filename):
    pass


@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        # 获取上传文件
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': '没有上传文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': '文件名为空'}), 400
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': '不支持的文件类型'}), 400

        # 保存文件
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        # 模拟人脸标记分析
        image = Image.open(upload_path)
        draw = ImageDraw.Draw(image)
        # 假设人脸位置为固定区域，实际中需调用分析模型
        draw.rectangle([50, 50, 150, 150], outline="red", width=3)
        result_path = os.path.join(app.config['RESULT_FOLDER'], f"result_{filename}")
        image.save(result_path)

        return jsonify({'status': 'success', 'result_image': result_path}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
