# 多维人脸分析系统 API 文档

## API 概述

该 API 提供了人脸分析的功能，支持多种分析方案，包括年龄预测、性别识别、情绪分析和种族识别等。

## 基础信息

- 基础URL: `http://your-domain/api/v1`
- 所有请求都应该包含 `Content-Type: application/json` 或 `multipart/form-data`（上传文件时）
- 响应格式统一为 JSON

## 认证

目前版本不需要认证。如需添加认证机制，请参考扩展建议部分。

## API 端点

### 1. 分析图片

**请求**

```
POST /analyze
Content-Type: multipart/form-data
```

**参数**

| 参数名 | 类型 | 必选 | 描述 |
|--------|------|------|------|
| image | File | 是 | 要分析的图片文件 |
| solution | String | 是 | 分析方案（deepface/facepp/dlib/insightface/mediapipe） |
| detection_options | JSON | 是 | 检测选项 |

detection_options 格式：
```json
{
    "age": boolean,
    "gender": boolean,
    "emotion": boolean,
    "race": boolean
}
```

**响应**

成功响应 (200):
```json
{
    "status": "success",
    "results": [
        {
            "id": 1,
            "gender": "男性",
            "age": 25,
            "emotion": "高兴",
            "race": "亚洲人"
        }
    ],
    "result_image": "/static/results/result_20241212_123456.jpg",
    "csv_file": "/static/results/analysis_20241212_123456.csv"
}
```

错误响应 (400/500):
```json
{
    "status": "error",
    "message": "错误描述",
    "error_code": "ERROR_CODE"
}
```

### 2. 获取支持的分析方案

**请求**

```
GET /solutions
```

**响应**

```json
{
    "status": "success",
    "solutions": {
        "deepface": {
            "id": "deepface",
            "name": "DeepFace",
            "description": "...",
            "features": ["年龄预测", "性别识别", "情绪分析", "种族识别"],
            "model_info": "VGG-Face/OpenCV backend"
        }
    }
}
```

### 3. 任务状态查询

**请求**

```
GET /task/{task_id}
```

**响应**

```json
{
    "status": "success",
    "task": {
        "id": "task_id",
        "status": "processing",
        "progress": 45,
        "result": null
    }
}
```

## 错误代码

| 错误代码 | 描述 |
|----------|------|
| FILE_TOO_LARGE | 文件超过大小限制 |
| INVALID_FILE_TYPE | 不支持的文件类型 |
| MODEL_NOT_FOUND | 模型文件未找到 |
| INVALID_OPTIONS | 无效的检测选项 |
| NO_FACE_DETECTED | 未检测到人脸 |
| ANALYSIS_ERROR | 分析过程出错 |

## 扩展建议

1. 添加认证机制
2. 实现批量处理
3. 添加自定义模型支持
4. 实现实时分析
5. 添加结果缓存机制

## SDK 示例

### Python

```python
import requests

def analyze_face(image_path, solution='deepface', options=None):
    if options is None:
        options = {'age': True, 'gender': True}
        
    files = {
        'image': open(image_path, 'rb')
    }
    
    data = {
        'solution': solution,
        'detection_options': json.dumps(options)
    }
    
    response = requests.post(
        'http://your-domain/api/v1/analyze',
        files=files,
        data=data
    )
    
    return response.json()
```

### JavaScript

```javascript
async function analyzeFace(imageFile, solution = 'deepface', options = null) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('solution', solution);
    formData.append('detection_options', JSON.stringify(options || {
        age: true,
        gender: true
    }));
    
    const response = await fetch('/api/v1/analyze', {
        method: 'POST',
        body: formData
    });
    
    return response.json();
}
```