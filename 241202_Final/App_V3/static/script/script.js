// static/js/script.js
// static/js/script.js
import { AnalysisController } from './controllers/AnalysisController.js';

document.addEventListener('DOMContentLoaded', () => {
    window.app = new AnalysisController();
});
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const previewImage = document.getElementById('previewImage');
    const resultImage = document.getElementById('resultImage');
    const resultTable = document.getElementById('resultTable');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const downloadSection = document.querySelector('.download-section');
    const downloadImage = document.getElementById('downloadImage');
    const downloadCSV = document.getElementById('downloadCSV');

    let currentResultImage = '';
    let currentCSVFile = '';

    // 方案配置数据
    const solutionConfigs = {
        'deepface': {
            name: 'DeepFace',
            description: 'DeepFace是一个流行的开源人脸分析解决方案，基于深度学习技术。优点是易于使用、功能全面，支持多种预训练模型。适合一般用途和原型开发。速度适中，准确率较好。',
            features: ['年龄预测', '性别识别', '情绪分析', '种族识别'],
            model_info: 'VGG-Face/OpenCV backend'
        },
        'facepp': {
            name: 'Face++',
            description: 'Face++是旷视科技开发的商业级人脸分析API。具有高精度的人脸检测和属性分析能力，服务稳定，适合商业应用。支持更细致的人脸特征分析。',
            features: ['年龄预测', '性别识别', '情绪分析', '颜值打分', '美学分析'],
            model_info: 'Commercial API/Dense CNN'
        },
        'dlib': {
            name: 'Dlib',
            description: 'Dlib是一个包含机器学习算法的C++工具包，其人脸分析模块以准确的人脸关键点检测而闻名。处理速度快，资源占用少，适合嵌入式系统和实时应用。',
            features: ['人脸检测', '关键点定位', '人脸对齐'],
            model_info: 'HOG/CNN detector'
        },
        'insightface': {
            name: 'InsightFace',
            description: 'InsightFace是基于MXNet的开源2D&3D人脸分析工具包，在人脸识别领域享有盛誉。采用SOTA的算法，具有很高的准确率。适合要求高精度的专业应用。',
            features: ['人脸检测', '人脸识别', '关键点检测', '属性分析'],
            model_info: 'ArcFace/RetinaFace'
        },
        'mediapipe': {
            name: 'MediaPipe',
            description: 'MediaPipe是Google开发的跨平台机器学习解决方案。其人脸分析模块轻量级、实时性好，适合移动端和Web应用。支持3D人脸网格和面部表情分析。',
            features: ['人脸检测', '3D网格重建', '表情分析'],
            model_info: 'BlazeFace/TFLite'
        }
    };

    // 获取页面元素
    const solutionSelect = document.getElementById('solution');
    const descriptionEl = document.getElementById('solution-description');
    const featuresEl = document.getElementById('solution-features');
    const modelEl = document.getElementById('solution-model');

    // 更新方案信息显示
    function updateSolutionInfo() {
        const selectedSolution = solutionSelect.value;
        const config = solutionConfigs[selectedSolution];

        if (config) {
            // 更新描述
            descriptionEl.textContent = config.description;

            // 更新特性列表
            featuresEl.innerHTML = `
                <h4>支持的功能:</h4>
                <ul class="feature-list">
                    ${config.features.map(feature => `<li>${feature}</li>`).join('')}
                </ul>
            `;

            // 更新模型信息
            modelEl.innerHTML = `
                <h4>技术细节:</h4>
                <div class="model-info">${config.model_info}</div>
            `;
        }
    }

    // 初始显示默认选中方案的信息
    if (solutionSelect) {
        updateSolutionInfo();
        solutionSelect.addEventListener('change', updateSolutionInfo);
    }

    // 图片选择事件
    imageInput.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            const reader = new FileReader();

            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
                resultImage.style.display = 'none';
                analyzeBtn.disabled = false;
            };

            reader.readAsDataURL(file);
        }
    });

    // 分析按钮点击事件
    analyzeBtn.addEventListener('click', function() {
        // 获取选中的检测选项
        const detectionOptions = {};
        document.querySelectorAll('input[name="detection"]:checked').forEach(checkbox => {
            detectionOptions[checkbox.value] = true;
        });

        // 检查是否至少选择了一个选项
        if (Object.keys(detectionOptions).length === 0) {
            alert('请至少选择一个检测选项！');
            return;
        }

        // 准备表单数据
        const formData = new FormData();
        formData.append('image', imageInput.files[0]);
        formData.append('solution', solutionSelect.value);
        formData.append('detection_options', JSON.stringify(detectionOptions));

        // 显示加载动画
        loadingOverlay.style.display = 'flex';

        // 发送请求
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // 显示结果图片
                resultImage.src = data.result_image;
                resultImage.style.display = 'block';
                previewImage.style.display = 'none';

                // 更新结果表格
                const tbody = resultTable.querySelector('tbody');
                tbody.innerHTML = '';
                data.results.forEach(result => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>#${result.id}</td>
                        <td>${result.gender}</td>
                        <td>${result.age}</td>
                        <td>${result.emotion}</td>
                        <td>${result.race}</td>
                    `;
                    tbody.appendChild(row);
                });

                // 保存当前的文件路径供下载使用
                currentResultImage = data.result_image;
                currentCSVFile = data.csv_file;

                // 显示下载按钮区域
                downloadSection.style.display = 'flex';
            } else {
                alert('分析失败：' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('发生错误，请重试！');
        })
        .finally(() => {
            loadingOverlay.style.display = 'none';
        });
    });

    // 下载结果图片
    downloadImage.addEventListener('click', function() {
        if (currentResultImage) {
            const link = document.createElement('a');
            link.href = currentResultImage;
            link.download = 'analysis_result.jpg';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });

    // 下载CSV文件
    downloadCSV.addEventListener('click', function() {
        if (currentCSVFile) {
            const link = document.createElement('a');
            link.href = currentCSVFile;
            link.download = 'analysis_result.csv';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });

    // 检查是否所有必需的元素都加载完成
    const requiredElements = [
        imageInput, analyzeBtn, previewImage, resultImage,
        resultTable, loadingOverlay, downloadSection,
        downloadImage, downloadCSV
    ];

    const missingElements = requiredElements.filter(element => !element);
    if (missingElements.length > 0) {
        console.error('Some required elements are missing:', missingElements);
    }
});