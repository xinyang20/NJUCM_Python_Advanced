class FaceAnalysisError(Exception):
    """人脸分析基础异常类"""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

class FileValidationError(FaceAnalysisError):
    """文件验证相关异常"""
    pass

class ModelNotFoundError(FaceAnalysisError):
    """模型未找到异常"""
    pass

class AnalysisError(FaceAnalysisError):
    """分析过程中的异常"""
    pass

class InvalidOptionsError(FaceAnalysisError):
    """无效的选项异常"""
    pass