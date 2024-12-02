import sys
import cv2
import dlib
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

# 初始化 Dlib 的人脸检测器和特征提取器
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多功能人脸识别系统")
        self.setGeometry(100, 100, 800, 600)

        # 创建用于显示视频的标签
        self.image_label = QLabel(self)
        self.image_label.resize(800, 600)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)

        # 设置定时器以刷新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # 转换为灰度图像
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 检测人脸
            faces = detector(gray)
            for face in faces:
                # 获取面部特征点
                landmarks = predictor(gray, face)
                # 绘制特征点
                for n in range(0, 68):
                    x = landmarks.part(n).x
                    y = landmarks.part(n).y
                    cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
            # 将图像转换为 Qt 格式并显示
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        self.cap.release()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())
