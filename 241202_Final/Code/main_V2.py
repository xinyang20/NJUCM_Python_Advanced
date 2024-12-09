import sys
import os
import cv2
import numpy as np
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                             QTextEdit, QFileDialog, QVBoxLayout, QHBoxLayout,
                             QWidget, QDialog, QMessageBox, QCheckBox)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt, QSettings

from deepface import DeepFace


class ConfigManager:
    """管理应用程序配置"""

    def __init__(self, app_name='FaceAnalysisApp'):
        self.settings = QSettings(f'{app_name}_config.ini', QSettings.IniFormat)

    def get(self, key, default=None):
        """获取配置项"""
        return self.settings.value(key, default)

    def set(self, key, value):
        """设置配置项"""
        self.settings.setValue(key, value)

    def save(self):
        """保存配置"""
        self.settings.sync()


class FaceAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 配置管理
        self.config = ConfigManager()

        # 初始化界面
        self.init_ui()

        # 初始化摄像头和定时器
        self.cap = None
        self.timer = QTimer()
        self.realtime_running = False
        self.current_image = None

        # 额外的检测选项
        self.detection_options = {
            'age': True,
            'gender': True,
            'emotion': True,
            'race': True
        }

        # 加载上次的配置
        self.load_config()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("多维人脸分析系统")
        self.setFixedSize(900, 700)  # 稍微增大窗口

        # 主窗口布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 图像显示区域
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(450)
        self.image_label.mousePressEvent = self.show_large_image
        self.main_layout.addWidget(self.image_label, 3)

        # 检测结果文本框
        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.result_text.setFont(QFont('微软雅黑', 10))
        self.main_layout.addWidget(self.result_text)

        # 功能按钮区域
        self.button_layout = QHBoxLayout()

        # 实时监测按钮
        self.start_button = QPushButton("启动实时检测", self)
        self.start_button.clicked.connect(self.toggle_realtime)
        self.button_layout.addWidget(self.start_button)

        # 图片检测按钮
        self.load_button = QPushButton("选择图片", self)
        self.load_button.clicked.connect(self.load_image)
        self.button_layout.addWidget(self.load_button)

        # 检测选项配置按钮
        self.config_button = QPushButton("检测选项", self)
        self.config_button.clicked.connect(self.show_detection_options)
        self.button_layout.addWidget(self.config_button)

        self.main_layout.addLayout(self.button_layout)

    def show_detection_options(self):
        """显示检测选项配置对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("检测选项")
        layout = QVBoxLayout()

        # 为每个检测选项创建复选框
        checkboxes = {}
        for option, default in self.detection_options.items():
            checkbox = QCheckBox(option.capitalize())
            checkbox.setChecked(default)
            checkboxes[option] = checkbox
            layout.addWidget(checkbox)

        def save_options():
            for option, checkbox in checkboxes.items():
                self.detection_options[option] = checkbox.isChecked()
            dialog.accept()

        save_button = QPushButton("保存")
        save_button.clicked.connect(save_options)
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def load_config(self):
        """加载上次的配置"""
        # 可以在这里加载上次的检测选项等
        pass

    def toggle_realtime(self):
        """启动/停止实时监测"""
        if self.realtime_running:
            self.stop_realtime()
        else:
            self.start_realtime()

    def start_realtime(self):
        """启动实时监测"""
        try:
            if self.cap is None:
                self.cap = cv2.VideoCapture(0)
                if not self.cap.isOpened():
                    raise IOError("无法打开摄像头")

            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
            self.realtime_running = True
            self.start_button.setText("停止实时检测")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"启动实时监测失败: {str(e)}")
            self.stop_realtime()

    def stop_realtime(self):
        """停止实时监测"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.timer.stop()
        self.realtime_running = False
        self.start_button.setText("启动实时检测")
        self.image_label.clear()

    def update_frame(self):
        """实时更新摄像头画面并绘制人脸框"""
        try:
            ret, frame = self.cap.read()
            if not ret:
                raise IOError("无法读取摄像头帧")

            # 转换为 RGB 格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 确定要执行的识别动作
            actions = [action for action, enabled in self.detection_options.items() if enabled]

            if not actions:
                self.result_text.setPlainText("请至少选择一种检测选项")
                return

            # 分析摄像头画面中的人脸
            analysis = DeepFace.analyze(
                img_path=rgb_frame,
                actions=actions,
                enforce_detection=False
            )

            self.process_face_analysis(frame, analysis)

        except Exception as e:
            print(f"实时分析出错: {e}")
            self.result_text.setPlainText(f"实时分析出错: {e}")

    def load_image(self):
        """加载图片并进行检测"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.jpg *.jpeg *.png)")
            if not file_path:
                return

            # 读取图片
            frame = cv2.imread(file_path)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 确定要执行的识别动作
            actions = [action for action, enabled in self.detection_options.items() if enabled]

            if not actions:
                self.result_text.setPlainText("请至少选择一种检测选项")
                return

            # 分析图片
            analysis = DeepFace.analyze(
                img_path=file_path,
                actions=actions,
                enforce_detection=False
            )

            self.process_face_analysis(frame, analysis)

        except Exception as e:
            self.result_text.setPlainText(f"分析图片出错: {e}")

    def process_face_analysis(self, frame, analysis):
        """处理人脸分析结果"""
        # 重置结果显示
        self.result_text.clear()

        if not isinstance(analysis, list):
            analysis = [analysis]  # 如果只有一个对象，包装成列表

        results = []  # 用于存储检测结果
        for idx, face in enumerate(analysis):
            region = face.get('region', {})
            x, y, w, h = region.get('x', 0), region.get('y', 0), region.get('w', 0), region.get('h', 0)

            # 绘制人脸框和序号
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"#{idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            result_items = [f"目标#{idx + 1}:"]

            # 性别
            if self.detection_options['gender']:
                gender_dict = face.get('gender', {})
                male_prob = gender_dict.get('Man', 0)
                female_prob = gender_dict.get('Woman', 0)
                if abs(male_prob - female_prob) > 20:
                    gender = "男性" if male_prob > female_prob else "女性"
                else:
                    gender = f"男性({male_prob:.1f}%) 女性({female_prob:.1f}%)"
                result_items.append(f"性别: {gender}")

            # 年龄
            if self.detection_options['age']:
                result_items.append(f"年龄: {face.get('age', '未知')}")

            # 情绪
            if self.detection_options['emotion']:
                emotion_translations = {
                    "neutral": "中性", "happy": "高兴", "sad": "悲伤",
                    "angry": "生气", "fear": "恐惧", "disgust": "厌恶",
                    "surprise": "惊讶"
                }
                emotion = face.get('dominant_emotion', '').lower()
                emotion_cn = emotion_translations.get(emotion, emotion)
                result_items.append(f"情绪: {emotion_cn}")

            # 种族
            if self.detection_options['race']:
                race_translations = {
                    "asian": "亚洲人", "white": "白人", "black": "黑人",
                    "middle eastern": "中东人", "latino hispanic": "拉丁裔",
                    "indian": "印度人"
                }
                race = face.get('dominant_race', '').lower()
                race_cn = race_translations.get(race, race)
                result_items.append(f"种族: {race_cn}")

            results.append(" ".join(result_items))

        # 在下方显示分类结果
        self.result_text.setPlainText("\n".join(results))

        # 将图片转换为 Qt 图像并显示
        qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(self.image_label.size(), Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.current_image = pixmap

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
        # 可以在这里保存配置
        self.config.save()


def main():
    app = QApplication(sys.argv)
    window = FaceAnalysisApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()