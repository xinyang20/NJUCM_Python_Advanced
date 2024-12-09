import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt
from deepface import DeepFace


class FaceAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("实时/图片检测 - 多对象分析")
        self.setFixedSize(800, 600)  # 锁定窗体大小

        # 主窗口布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # 图像显示区域，占75%的高度
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(400)
        self.image_label.mousePressEvent = self.show_large_image  # 添加点击事件
        self.main_layout.addWidget(self.image_label, 3)  # 权重3表示75%

        # 底部区域布局，占25%的高度
        self.bottom_layout = QVBoxLayout()

        # 检测结果文本框
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.bottom_layout.addWidget(self.result_text)

        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.start_button = QPushButton("实时监测", self)
        self.start_button.clicked.connect(self.toggle_realtime)
        self.button_layout.addWidget(self.start_button)

        self.load_button = QPushButton("选择图片", self)
        self.load_button.clicked.connect(self.load_image)
        self.button_layout.addWidget(self.load_button)

        self.bottom_layout.addLayout(self.button_layout)

        self.main_layout.addLayout(self.bottom_layout, 1)  # 权重1表示25%

        # 摄像头和定时器
        self.cap = None
        self.timer = QTimer()
        self.realtime_running = False  # 实时监测状态标志

        # 用于存储当前显示的图片
        self.current_image = None

    def toggle_realtime(self):
        """启动/停止实时监测"""
        if self.realtime_running:
            self.stop_realtime()
        else:
            self.start_realtime()

    def start_realtime(self):
        """启动实时监测"""
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        self.realtime_running = True
        self.start_button.setText("停止监测")

    def stop_realtime(self):
        """停止实时监测"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.timer.stop()
        self.realtime_running = False
        self.start_button.setText("实时监测")

    def update_frame(self):
        """实时更新摄像头画面并绘制人脸框"""
        ret, frame = self.cap.read()
        if not ret:
            print("无法读取摄像头帧")
            return

        # 转换为 RGB 格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 初始化结果显示
        self.result_text.clear()

        try:
            # 分析摄像头画面中的人脸
            analysis = DeepFace.analyze(
                img_path=rgb_frame,
                actions=["age", "gender", "emotion", "race"],
                enforce_detection=False
            )

            if not isinstance(analysis, list):
                analysis = [analysis]  # 如果只有一个对象，包装成列表

            results = []  # 用于存储检测结果
            for idx, face in enumerate(analysis):
                region = face.get('region', {})
                x, y, w, h = region.get('x', 0), region.get('y', 0), region.get('w', 0), region.get('h', 0)

                # 绘制人脸框和序号
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"#{idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 处理性别
                gender_dict = face['gender']
                male_prob = gender_dict['Man']
                female_prob = gender_dict['Woman']
                if abs(male_prob - female_prob) > 20:
                    gender = "男性" if male_prob > female_prob else "女性"
                else:
                    gender = f"男性({male_prob:.1f}%) 女性({female_prob:.1f}%)"

                # 翻译情绪和种族
                emotion_translations = {
                    "neutral": "中性",
                    "happy": "高兴",
                    "sad": "悲伤",
                    "angry": "生气",
                    "fear": "恐惧",
                    "disgust": "厌恶",
                    "surprise": "惊讶"
                }
                race_translations = {
                    "asian": "亚洲人",
                    "white": "白人",
                    "black": "黑人",
                    "middle eastern": "中东人",
                    "latino hispanic": "拉丁裔",
                    "indian": "印度人"
                }
                emotion_cn = emotion_translations.get(face['dominant_emotion'].lower(), face['dominant_emotion'])
                race_cn = race_translations.get(face['dominant_race'].lower(), face['dominant_race'])

                # 拼接结果
                results.append(f"目标#{idx + 1}: 性别: {gender}, 年龄: {face['age']}, 情绪: {emotion_cn}, 种族: {race_cn}")

            # 在下方显示分类结果
            self.result_text.setPlainText("\n".join(results))

        except Exception as e:
            print(f"实时分析出错: {e}")

        # 将摄像头画面转换为 Qt 图像并显示
        qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(self.image_label.size(), Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.current_image = pixmap

    def load_image(self):
        """加载图片并进行检测"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.jpg *.jpeg *.png)")
        if not file_path:
            return

        # 读取图片
        frame = cv2.imread(file_path)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 初始化结果显示
        self.result_text.clear()

        try:
            # 分析图片
            analysis = DeepFace.analyze(
                img_path=file_path,
                actions=["age", "gender", "emotion", "race"],
                enforce_detection=False
            )

            if not isinstance(analysis, list):
                analysis = [analysis]  # 如果只有一个对象，包装成列表

            results = []  # 用于存储检测结果
            for idx, face in enumerate(analysis):
                region = face.get('region', {})
                x, y, w, h = region.get('x', 0), region.get('y', 0), region.get('w', 0), region.get('h', 0)

                # 绘制人脸框和序号
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"#{idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # 处理性别
                gender_dict = face['gender']
                male_prob = gender_dict['Man']
                female_prob = gender_dict['Woman']
                if abs(male_prob - female_prob) > 20:
                    gender = "男性" if male_prob > female_prob else "女性"
                else:
                    gender = f"男性({male_prob:.1f}%) 女性({female_prob:.1f}%)"

                # 翻译情绪和种族
                emotion_translations = {
                    "neutral": "中性",
                    "happy": "高兴",
                    "sad": "悲伤",
                    "angry": "生气",
                    "fear": "恐惧",
                    "disgust": "厌恶",
                    "surprise": "惊讶"
                }
                race_translations = {
                    "asian": "亚洲人",
                    "white": "白人",
                    "black": "黑人",
                    "middle eastern": "中东人",
                    "latino hispanic": "拉丁裔",
                    "indian": "印度人"
                }
                emotion_cn = emotion_translations.get(face['dominant_emotion'].lower(), face['dominant_emotion'])
                race_cn = race_translations.get(face['dominant_race'].lower(), face['dominant_race'])

                # 拼接结果
                results.append(f"目标#{idx + 1}: 性别: {gender}, 年龄: {face['age']}, 情绪: {emotion_cn}, 种族: {race_cn}")

            # 在下方显示分类结果
            self.result_text.setPlainText("\n".join(results))

            # 将图片转换为 Qt 图像并显示
            qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image).scaled(self.image_label.size(), Qt.KeepAspectRatio)
            self.image_label.setPixmap(pixmap)
            self.current_image = pixmap

        except Exception as e:
            self.result_text.setPlainText(f"分析图片出错: {e}")

    def show_large_image(self, event):
        """点击图片查看放大的图片"""
        if self.current_image is not None:
            dialog = QDialog(self)
            dialog.setWindowTitle("放大图片")
            dialog.setFixedSize(800, 600)
            layout = QVBoxLayout(dialog)

            label = QLabel(dialog)
            label.setPixmap(self.current_image.scaled(780, 580, Qt.KeepAspectRatio))
            layout.addWidget(label)

            dialog.exec_()

    def closeEvent(self, event):
        """释放资源"""
        if self.cap is not None:
            self.cap.release()
        self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceAnalysisApp()
    window.show()
    sys.exit(app.exec_())
