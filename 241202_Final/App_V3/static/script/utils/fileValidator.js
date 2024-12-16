// utils/fileValidator.js
class FileValidator {
    constructor() {
        this.maxSize = 16 * 1024 * 1024; // 16MB
        this.allowedTypes = new Set(['image/jpeg', 'image/png']);
        this.minDimensions = { width: 100, height: 100 };
        this.maxDimensions = { width: 4096, height: 4096 };
    }

    async validateFile(file) {
        // 检查文件是否存在
        if (!file) {
            throw new Error('请选择文件');
        }

        // 检查文件类型
        if (!this.allowedTypes.has(file.type)) {
            throw new Error('只支持 JPG/PNG 格式图片');
        }

        // 检查文件大小
        if (file.size > this.maxSize) {
            throw new Error('文件大小不能超过 16MB');
        }

        // 检查图片尺寸
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.src = URL.createObjectURL(file);

            img.onload = () => {
                URL.revokeObjectURL(img.src);

                if (img.width < this.minDimensions.width ||
                    img.height < this.minDimensions.height) {
                    reject(new Error('图片尺寸过小，最小要求 100x100'));
                }

                if (img.width > this.maxDimensions.width ||
                    img.height > this.maxDimensions.height) {
                    reject(new Error('图片尺寸过大，最大支持 4096x4096'));
                }

                resolve(true);
            };

            img.onerror = () => {
                URL.revokeObjectURL(img.src);
                reject(new Error('图片加载失败，请检查文件是否损坏'));
            };
        });
    }
}