# config.py

import os
from datetime import timedelta


class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
    RESULT_FOLDER = os.path.join(BASE_DIR, 'static/results')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB 限制
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # 日志配置
    LOG_FOLDER = os.path.join(BASE_DIR, 'logs')
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

    # Redis 配置（用于任务队列）
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Celery 配置
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_TASK_TRACK_STARTED = True

    # 模型下载链接配置
    MODEL_PATHS = {
        'deepface': {
            'path': os.path.join(BASE_DIR, 'models/deepface'),
            'download_url': 'https://github.com/serengil/deepface_models/releases/download/v1.0/facial_expression_model_weights.h5'
        },
        'face++': {
            'path': os.path.join(BASE_DIR, 'models/facepp'),
            'api_key': os.environ.get('FACEPP_API_KEY'),
            'api_secret': os.environ.get('FACEPP_API_SECRET')
        },
        'dlib': {
            'path': os.path.join(BASE_DIR, 'models/dlib'),
            'download_url': 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
        },
        'insightface': {
            'path': os.path.join(BASE_DIR, 'models/insightface'),
            'download_url': 'https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip'
        },
        'mediapipe': {
            'path': os.path.join(BASE_DIR, 'models/mediapipe'),
            # MediaPipe 模型通过 pip 安装自动下载
        }
    }

    @staticmethod
    def init_app(app):
        # 创建必要的文件夹
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.RESULT_FOLDER, exist_ok=True)
        os.makedirs(Config.LOG_FOLDER, exist_ok=True)

        # 创建模型文件夹
        for model in Config.MODEL_PATHS.values():
            if 'path' in model:
                os.makedirs(model['path'], exist_ok=True)