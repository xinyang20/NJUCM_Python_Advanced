import sys
import cv2
import mediapipe as mp
from deepface import DeepFace
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer


class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多功能人脸识别系统")
        self.setGeometry(100, 100, 800, 600)

        # Mediapipe 初始化
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_draw = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection()

        # 创建视频显示标签
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

        # 定时器刷新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def analyze_face(self, frame):
        """使用 DeepFace 分析面部属性"""
        try:
            results = DeepFace.analyze(
                frame, actions=["age", "gender", "emotion", "race"], enforce_detection=False
            )
            return results
        except Exception as e:
            print(f"DeepFace 分析失败: {e}")
            return None

    def update_frame(self):
        """更新摄像头帧"""
        ret, frame = self.cap.read()
        if not ret:
            return

        # 转换为 RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Mediapipe 人脸检测
        results = self.face_detection.process(rgb_frame)
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x1, y1 = int(bbox.xmin * w), int(bbox.ymin * h)
                x2, y2 = int((bbox.xmin + bbox.width) * w), int((bbox.ymin + bbox.height) * h)

                # 绘制人脸检测框
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # 截取人脸区域进行分析
                face_crop = rgb_frame[y1:y2, x1:x2]
                face_analysis = self.analyze_face(face_crop)
                if face_analysis:
                    # 在检测框上显示年龄、性别和表情
                    age = face_analysis["age"]
                    gender = face_analysis["gender"]
                    emotion = face_analysis["dominant_emotion"]
                    text = f"Age: {age}, Gender: {gender}, Emotion: {emotion}"
                    cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 转换为 Qt 格式显示
        qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_BGR888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        """释放资源"""
        self.cap.release()
        self.face_detection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())
