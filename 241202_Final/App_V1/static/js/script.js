document.addEventListener('DOMContentLoaded', function () {
    const solutionSelect = document.getElementById('solution');
    const detectionOptionsContainer = document.querySelector('.detection-options');
    const imageInput = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const previewImage = document.getElementById('previewImage');
    const resultTableBody = document.querySelector('#resultTable tbody');

    /**
     * 更新检测选项
     * 根据选择的模型 ID，动态加载该模型支持的检测选项
     */
    function updateDetectionOptions(modelId) {
        fetch(`/get_features/${modelId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // 动态生成检测选项
                    detectionOptionsContainer.innerHTML = `
                        <h3>检测选项：</h3>
                        ${data.features.map(feature => `
                            <label>
                                <input type="checkbox" name="detection" value="${feature}" checked> ${feature}
                            </label>
                        `).join('')}
                    `;
                } else {
                    alert(data.message || '无法加载检测选项，请稍后重试！');
                }
            })
            .catch(error => {
                console.error('Error loading detection options:', error);
                alert('加载检测选项时发生错误，请检查网络连接！');
            });
    }

    /**
     * 初始化页面
     * 默认加载第一个模型的检测选项
     */
    if (solutionSelect) {
        updateDetectionOptions(solutionSelect.value);

        solutionSelect.addEventListener('change', function () {
            updateDetectionOptions(this.value);
        });
    }

    /**
     * 预览用户上传的图片
     */
    imageInput.addEventListener('change', function (e) {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];

            // 检查文件类型是否允许
            const allowedExtensions = ['png', 'jpg', 'jpeg'];
            const fileExtension = file.name.split('.').pop().toLowerCase();
            if (!allowedExtensions.includes(fileExtension)) {
                alert('仅支持 PNG、JPG、JPEG 格式的图片！');
                imageInput.value = ''; // 清空文件输入
                return;
            }

            const reader = new FileReader();
            reader.onload = function (e) {
                previewImage.src = e.target.result;
                previewImage.style.display = 'block';
                analyzeBtn.disabled = false; // 启用分析按钮
            };
            reader.readAsDataURL(file);
        }
    });

    /**
     * 模拟分析功能
     * 此处可以通过实际调用后端分析 API 完成具体分析
     */
    analyzeBtn.addEventListener('click', function () {
        const selectedDetections = [];
        document.querySelectorAll('input[name="detection"]:checked').forEach(input => {
            selectedDetections.push(input.value);
        });

        if (selectedDetections.length === 0) {
            alert('请至少选择一个检测选项！');
            return;
        }

        alert(`模拟分析：上传图片，选中检测选项：${selectedDetections.join(', ')}`);

        // TODO: 添加实际分析逻辑，调用后端 API 处理图片
        // 示例:
        // fetch('/analyze', { method: 'POST', body: formData }).then(...)

        // 清空结果表格并添加测试数据
        resultTableBody.innerHTML = `
            <tr>
                <td>性别</td>
                <td>男性</td>
            </tr>
            <tr>
                <td>年龄</td>
                <td>25</td>
            </tr>
            <tr>
                <td>情绪</td>
                <td>高兴</td>
            </tr>
            <tr>
                <td>种族</td>
                <td>亚洲</td>
            </tr>
        `;
    });
    analyzeBtn.addEventListener('click', function () {
        const file = imageInput.files[0];
        if (!file) {
            alert('请先上传图片！');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        // 显示加载中提示
        const loadingText = document.getElementById('loading');
        loadingText.style.display = 'block';
        previewImage.style.display = 'none'; // 隐藏图片

        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                loadingText.style.display = 'none'; // 隐藏加载提示

                if (data.status === 'success') {
                    previewImage.src = data.result_image + '?' + new Date().getTime(); // 强制刷新缓存
                    previewImage.style.display = 'block'; // 显示标记后图片
                } else {
                    alert(data.message || '分析失败，请稍后重试！');
                }
            })
            .catch(error => {
                loadingText.style.display = 'none';
                console.error('分析失败:', error);
                alert('分析过程中出现错误，请稍后重试！');
            });
    });

});
