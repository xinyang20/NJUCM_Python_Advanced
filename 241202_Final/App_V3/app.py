from flask import Flask, render_template, request, jsonify, send_file
import cv2
import numpy as np
from deepface import DeepFace
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from celery import Celery
import logging
from logging.handlers import TimedRotatingFileHandler
import redis
from functools import wraps

# 初始化 Flask 应用
app = Flask(__name__)


# 基础配置
# app.py 文件中的 Config 类定义

class Config:
    # 基础配置
    UPLOAD_FOLDER = 'static/uploads'
    RESULT_FOLDER = 'static/results'
    LOG_FOLDER = 'logs'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 限制
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # 模型配置
    MODEL_PATHS = {
        'DeepFace': {
            'id': 'deepface',
            'name': 'DeepFace',
            'description': 'DeepFace是一个流行的开源人脸分析解决方案，基于深度学习技术。',
            'features': ['年龄预测', '性别识别', '情绪分析', '种族识别'],
            'model_info': 'VGG-Face/OpenCV backend'
        },
        'Face++': {
            'id': 'facepp',
            'name': 'Face++',
            'description': 'Face++是旷视科技开发的商业级人脸分析API。',
            'features': ['年龄预测', '性别识别', '情绪分析', '颜值打分'],
            'model_info': 'Commercial API'
        },
        'Dlib': {
            'id': 'dlib',
            'name': 'Dlib',
            'description': 'Dlib是一个包含机器学习算法的C++工具包。',
            'features': ['人脸检测', '关键点定位', '人脸对齐'],
            'model_info': 'HOG/CNN detector'
        },
        'InsightFace': {
            'id': 'insightface',
            'name': 'InsightFace',
            'description': 'InsightFace是基于MXNet的开源2D&3D人脸分析工具包。',
            'features': ['人脸检测', '人脸识别', '关键点检测'],
            'model_info': 'ArcFace/RetinaFace'
        },
        'MediaPipe': {
            'id': 'mediapipe',
            'name': 'MediaPipe',
            'description': 'MediaPipe是Google开发的跨平台机器学习解决方案。',
            'features': ['人脸检测', '3D网格重建', '表情分析'],
            'model_info': 'BlazeFace/TFLite'
        }
    }

    # Redis 配置（用于任务队列）
    REDIS_URL = 'redis://localhost:6379/0'

    # Celery 配置
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL


app.config.from_object(Config)

# 创建必要的文件夹
for folder in [Config.UPLOAD_FOLDER, Config.RESULT_FOLDER, Config.LOG_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# 初始化 Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# 初始化 Redis
redis_client = redis.from_url(Config.REDIS_URL)


# 配置日志
def setup_logger():
    log_file = os.path.join(Config.LOG_FOLDER, 'app.log')
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '[%(filename)s:%(lineno)d] - %(message)s'
    )

    file_handler = TimedRotatingFileHandler(
        log_file, when='midnight', interval=1,
        backupCount=30, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger('face_analysis')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()


# 自定义异常类
class AnalysisError(Exception):
    pass


class FileValidationError(Exception):
    pass


class ModelNotFoundError(Exception):
    pass


# 工具函数
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def validate_file(file):
    if not file:
        raise FileValidationError("未上传文件")
    if not allowed_file(file.filename):
        raise FileValidationError("不支持的文件类型")
    return True


def log_operation(operation_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.now()
            request_ip = request.remote_addr
            user_agent = request.user_agent.string

            logger.info(
                f"Operation started: {operation_type} - "
                f"IP: {request_ip} - UA: {user_agent}"
            )

            try:
                result = f(*args, **kwargs)
                logger.info(
                    f"Operation completed: {operation_type} - "
                    f"IP: {request_ip} - "
                    f"Duration: {datetime.now() - start_time}"
                )
                return result
            except Exception as e:
                logger.error(
                    f"Operation failed: {operation_type} - "
                    f"IP: {request_ip} - Error: {str(e)}"
                )
                raise

        return decorated_function

    return decorator


# Celery 任务
@celery.task(bind=True)
def analyze_image_task(self, file_path, solution, options):
    try:
        frame = cv2.imread(file_path)
        if frame is None:
            raise AnalysisError("无法读取图片")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 更新进度
        self.update_state(state='PROGRESS', meta={'progress': 30})

        # 分析图片
        analysis = DeepFace.analyze(
            img_path=rgb_frame,
            actions=list(options.keys()),
            enforce_detection=False,
            detector_backend='opencv'
        )

        if not isinstance(analysis, list):
            analysis = [analysis]

        # 处理结果
        self.update_state(state='PROGRESS', meta={'progress': 60})

        results = []
        for idx, face in enumerate(analysis):
            # 处理人脸区域
            region = face.get('region', {})
            x, y, w, h = region.get('x', 0), region.get('y', 0), \
                region.get('w', 0), region.get('h', 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # 整理结果
            result = {
                'id': idx + 1,
                'gender': "男性" if face.get('gender', {}).get('Man', 0) > 50 else "女性",
                'age': face.get('age', '未知'),
                'emotion': face.get('dominant_emotion', '未知'),
                'race': face.get('dominant_race', '未知')
            }
            results.append(result)

        # 保存结果
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_image = f"result_{timestamp}.jpg"
        result_csv = f"analysis_{timestamp}.csv"

        cv2.imwrite(os.path.join(Config.RESULT_FOLDER, result_image), frame)
        pd.DataFrame(results).to_csv(
            os.path.join(Config.RESULT_FOLDER, result_csv),
            index=False, encoding='utf-8-sig'
        )

        self.update_state(state='PROGRESS', meta={'progress': 100})

        return {
            'status': 'success',
            'results': results,
            'result_image': f'/static/results/{result_image}',
            'csv_file': f'/static/results/{result_csv}'
        }

    except Exception as e:
        logger.error(f"Analysis task error: {str(e)}")
        return {'status': 'error', 'message': str(e)}


# 路由
@app.route('/')
def index():
    """主页路由"""
    return render_template(
        'index.html',
        solutions=Config.MODEL_PATHS
    )


@app.route('/analyze', methods=['POST'])
@log_operation('analyze_image')
def analyze():
    try:
        # 验证文件
        file = request.files.get('image')
        validate_file(file)

        # 获取参数
        solution = request.form.get('solution', 'deepface')
        options = json.loads(request.form.get('detection_options', '{}'))

        if not options:
            raise ValueError("请至少选择一个检测选项")

        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"upload_{timestamp}.jpg"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        # 创建异步任务
        task = analyze_image_task.delay(file_path, solution, options)

        return jsonify({
            'status': 'success',
            'task_id': task.id
        })

    except FileValidationError as e:
        logger.warning(f"File validation error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

    except Exception as e:
        logger.error(f"Analyze error: {str(e)}")
        return jsonify({'status': 'error', 'message': "处理失败"}), 500


@app.route('/task/<task_id>')
def get_task_status(task_id):
    task = analyze_image_task.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'progress': 0,
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'progress': 100,
            'result': task.get()
        }
    else:
        response = {
            'state': task.state,
            'progress': task.info.get('progress', 0) if task.info else 0,
        }

    return jsonify(response)


@app.route('/download/<path:filename>')
@log_operation('download_file')
def download_file(filename):
    try:
        return send_file(
            os.path.join(Config.RESULT_FOLDER, filename),
            as_attachment=True
        )
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'status': 'error', 'message': "下载失败"}), 404


# 清理任务
@celery.task
def cleanup_old_files():
    try:
        threshold = datetime.now() - timedelta(hours=24)
        cleaned = 0

        for folder in [Config.UPLOAD_FOLDER, Config.RESULT_FOLDER]:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.getctime(filepath) < threshold.timestamp():
                    os.remove(filepath)
                    cleaned += 1

        logger.info(f"Cleaned {cleaned} old files")

    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")


# 主程序
if __name__ == '__main__':
    app.run(debug=True)