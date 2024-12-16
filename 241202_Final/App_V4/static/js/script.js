// static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const previewImage = document.getElementById('previewImage');
    const resultImage = document.getElementById('resultImage');
    const resultTable = document.getElementById('resultTable');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const downloadSection = document.querySelector('.download-section');

    let currentResultImage = '';
    let currentCSVFile = '';

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
                currentResultImage = data.result_image.split('/').pop();
                currentCSVFile = data.csv_file.split('/').pop();

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

    // 修复的下载按钮点击事件
    document.getElementById('downloadResults').addEventListener('click', function() {
        if (currentResultImage && currentCSVFile) {
            // 下载图片
            window.location.href = `/download/${currentResultImage}`;

            // 延迟一下再下载CSV，避免浏览器阻止多个下载
            setTimeout(() => {
                window.location.href = `/download/${currentCSVFile}`;
            }, 1000);
        } else {
            alert('没有可下载的结果文件');
        }
    });
});