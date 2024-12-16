// state/analysisState.js
class AnalysisState {
    constructor() {
        this._state = {
            currentImage: null,          // 当前选择的图片文件
            imagePreview: null,          // 图片预览URL
            analysisResults: null,       // 分析结果
            selectedSolution: 'deepface', // 选中的分析方案
            detectionOptions: new Set(['age', 'gender', 'emotion', 'race']), // 检测选项
            isProcessing: false,         // 是否正在处理
            error: null,                 // 错误信息
            taskId: null                 // 任务ID
        };

        this._listeners = new Set();     // 状态监听器
    }

    // 订阅状态变化
    subscribe(listener) {
        this._listeners.add(listener);
        return () => this._listeners.delete(listener);
    }

    // 通知所有监听器
    _notify() {
        this._listeners.forEach(listener => listener(this._state));
    }

    // 获取当前状态
    getState() {
        return {...this._state};
    }

    // 更新状态
    setState(newState) {
        this._state = {
            ...this._state,
            ...newState
        };
        this._notify();
    }

    // 重置状态
    reset() {
        if (this._state.imagePreview) {
            URL.revokeObjectURL(this._state.imagePreview);
        }
        this._state = new AnalysisState()._state;
        this._notify();
    }
}

