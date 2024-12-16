// controllers/AnalysisController.js
class AnalysisController {
    constructor() {
        this.state = new AnalysisState();
        this.fileValidator = new FileValidator();
        this.init();
    }

    init() {
        // 初始化UI元素引用
        this.elements = {
            imageInput: document.getElementById('imageInput'),
            analyzeBtn: document.getElementById('analyzeBtn'),
            previewImage: document.getElementById('previewImage'),
            resultImage: document.getElementById('resultImage'),
            resultTable: document.getElementById('resultTable'),
            loadingOverlay: document.getElementById('loadingOverlay'),
            solutionSelect: document.getElementById('solution'),
            detectionOptions: document.querySelectorAll('input[name="detection"]')
        };

        // 绑定事件处理
        this._bindEvents();

        // 订阅状态变化
        this.state.subscribe(this._handleStateChange.bind(this));
    }

    _bindEvents() {
        // 文件选择
        this.elements.imageInput.addEventListener('change',
            this._handleFileSelect.bind(this));

        // 分析按钮
        this.elements.analyzeBtn.addEventListener('click',
            this._handleAnalyzeClick.bind(this));

        // 方案选择
        this.elements.solutionSelect.addEventListener('change',
            this._handleSolutionChange.bind(this));

        // 检测选项
        this.elements.detectionOptions.forEach(option => {
            option.addEventListener('change',
                this._handleOptionChange.bind(this));
        });
    }

    // 处理文件选择
    async _handleFileSelect(event) {
        try {
            const file = event.target.files[0];
            if (!file) return;

            // 验证文件
            await this.fileValidator.validateFile(file);

            // 更新状态
            this.state.setState({
                currentImage: file,
                imagePreview: URL.createObjectURL(file),
                error: null
            });
        } catch (error) {
            this.state.setState({
                error: error.message,
                currentImage: null,
                imagePreview: null
            });

            // 重置文件输入
            event.target.value = '';
        }
    }

    // 处理分析按钮点击
    async _handleAnalyzeClick() {
        const state = this.state.getState();

        if (!state.currentImage) {
            this.state.setState({ error: '请先选择图片' });
            return;
        }

        if (state.detectionOptions.size === 0) {
            this.state.setState({ error: '请至少选择一个检测选项' });
            return;
        }

        try {
            this.state.setState({ isProcessing: true, error: null });

            const formData = new FormData();
            formData.append('image', state.currentImage);
            formData.append('solution', state.selectedSolution);
            formData.append('detection_options',
                JSON.stringify(Array.from(state.detectionOptions)));

            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.status === 'success') {
                this.state.setState({
                    analysisResults: data.results,
                    taskId: data.taskId
                });
            } else {
                throw new Error(data.message || '分析失败');
            }
        } catch (error) {
            this.state.setState({ error: error.message });
        } finally {
            this.state.setState({ isProcessing: false });
        }
    }

    // 状态变化处理
    _handleStateChange(state) {
        // 更新预览图片
        this.elements.previewImage.src = state.imagePreview || '';
        this.elements.previewImage.style.display =
            state.imagePreview ? 'block' : 'none';

        // 更新分析按钮状态
        this.elements.analyzeBtn.disabled =
            !state.currentImage || state.isProcessing;

        // 更新加载状态
        this.elements.loadingOverlay.style.display =
            state.isProcessing ? 'flex' : 'none';

        // 更新错误提示
        if (state.error) {
            this._showError(state.error);
        }

        // 更新分析结果
        if (state.analysisResults) {
            this._updateResults(state.analysisResults);
        }
    }

    // 显示错误提示
    _showError(message) {
        // 这里可以使用你喜欢的提示组件
        alert(message);
    }

    // 更新结果显示
    _updateResults(results) {
        const tbody = this.elements.resultTable.querySelector('tbody');
        tbody.innerHTML = '';

        results.forEach(result => {
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
    }
}