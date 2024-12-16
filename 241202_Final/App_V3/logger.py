import logging
import logging.handlers
import os
from datetime import datetime
from flask import request, has_request_context
from config import Config


class RequestFormatter(logging.Formatter):
    """自定义日志格式化器，添加请求相关信息"""

    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
            record.user_agent = request.user_agent.string
        else:
            record.url = None
            record.remote_addr = None
            record.method = None
            record.user_agent = None

        return super().format(record)


def setup_logger(app):
    """设置应用日志"""

    # 创建日志文件路径
    log_file = os.path.join(
        Config.LOG_FOLDER,
        f'app_{datetime.now().strftime("%Y-%m-%d")}.log'
    )

    # 设置日志格式
    formatter = RequestFormatter(
        '%(asctime)s - %(remote_addr)s - %(method)s - %(url)s - '
        '%(user_agent)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 文件处理器 - 按日期轮转
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when='midnight', interval=1,
        backupCount=30, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 配置根日志记录器
    app.logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    return app.logger


# 日志装饰器
def log_operation(operation_type):
    """记录操作日志的装饰器"""

    def decorator(f):
        from functools import wraps

        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app, request

            # 记录操作开始
            current_app.logger.info(
                f"Operation started: {operation_type} - "
                f"IP: {request.remote_addr} - "
                f"User-Agent: {request.user_agent}"
            )

            try:
                result = f(*args, **kwargs)
                # 记录操作成功
                current_app.logger.info(
                    f"Operation completed: {operation_type} - "
                    f"IP: {request.remote_addr}"
                )
                return result
            except Exception as e:
                # 记录操作失败
                current_app.logger.error(
                    f"Operation failed: {operation_type} - "
                    f"IP: {request.remote_addr} - "
                    f"Error: {str(e)}"
                )
                raise

        return decorated_function

    return decorator