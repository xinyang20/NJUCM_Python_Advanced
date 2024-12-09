import sys
import os
import cv2
import numpy as np
import json
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton,
                           QFileDialog, QVBoxLayout, QHBoxLayout, QWidget,
                           QDialog, QMessageBox, QCheckBox, QProgressBar,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QSpinBox, QDialogButtonBox, QFormLayout)
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor
from PyQt5.QtCore import QTimer, Qt, QSettings, pyqtSignal, QObject

from deepface import DeepFace

class ProgressSignal(QObject):
    """用于发送进度信号的类"""
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

class ImageSizeDialog(QDialog):
    """自定义图片尺寸对话框"""

    def __init__(self, parent=None, current_width=800, current_height=600):
        super().__init__(parent)
        self.setWindowTitle("设置查看图片尺寸")

        layout = QFormLayout(self)

        # 宽度输入
        self.width_spin = QSpinBox(self)
        self.width_spin.setRange(400, 3840)  # 设置合理的范围
        self.width_spin.setValue(current_width)
        layout.addRow("宽度:", self.width_spin)

        # 高度输入
        self.height_spin = QSpinBox(self)
        self.height_spin.setRange(300, 2160)
        self.height_spin.setValue(current_height)
        layout.addRow("高度:", self.height_spin)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_size(self):
        return self.width_spin.value(), self.height_spin.value()

class ConfigManager:
    """管理应用程序配置"""
    def __init__(self, app_name='FaceAnalysisApp'):
        self.settings = QSettings(f'{app_name}_config.ini', QSettings.IniFormat)

    def get(self, key, default=None):
        return self.settings.value(key, default)

    def set(self, key, value):
        self.settings.setValue(key, value)

    def save(self):
        self.settings.sync()


class FaceAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

        # 图片查看设置
        self.view_width = self.config.get('view_width', 800)
        self.view_height = self.config.get('view_height', 600)

        # 初始化界面
        self.init_ui()

        # 初始化摄像头和定时器
        self.cap = None
        self.timer = QTimer()
        self.realtime_running = False
        self.current_image = None

        # 进度信号
        self.progress_signal = ProgressSignal()
        self.progress_signal.progress.connect(self.update_progress)
        self.progress_signal.finished.connect(self.hide_progress)
        self.progress_signal.error.connect(self.show_error)

        # 检测选项（使用中文）
        self.detection_options = {
            '年龄检测': True,
            '性别检测': True,
            '情绪检测': True,
            '种族检测': True
        }

        # 选项映射（中文到英文）
        self.option_mapping = {
            '年龄检测': 'age',
            '性别检测': 'gender',
            '情绪检测': 'emotion',
            '种族检测': 'race'
        }

        self.load_config()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("多维人脸分析系统")
        self.setFixedSize(1000, 800)

        # 主窗口布局
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 图像显示区域
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(500)
        self.image_label.mousePressEvent = self.show_large_image
        self.main_layout.addWidget(self.image_label, 3)

        # 进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.main_layout.addWidget(self.progress_bar)

        # 结果表格
        self.result_table = QTableWidget(self)
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(['序号', '性别', '年龄', '情绪', '种族'])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.setMinimumHeight(200)
        self.main_layout.addWidget(self.result_table)

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
        """显示检测选项配置对话框（使用中文）"""
        dialog = QDialog(self)
        dialog.setWindowTitle("检测选项设置")
        layout = QVBoxLayout()

        # 使用中文选项创建复选框
        checkboxes = {}
        for option, default in self.detection_options.items():
            checkbox = QCheckBox(option)
            checkbox.setChecked(default)
            checkboxes[option] = checkbox
            layout.addWidget(checkbox)

        def save_options():
            for option, checkbox in checkboxes.items():
                self.detection_options[option] = checkbox.isChecked()
            dialog.accept()

        save_button = QPushButton("保存设置")
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

    def process_face_analysis(self, frame, analysis):
        """处理人脸分析结果"""
        # 清空表格
        self.result_table.setRowCount(0)

        if not isinstance(analysis, list):
            analysis = [analysis]

        # 设置表格行数
        self.result_table.setRowCount(len(analysis))

        # 情绪翻译字典
        emotion_translations = {
            "neutral": "中性", "happy": "高兴", "sad": "悲伤",
            "angry": "生气", "fear": "恐惧", "disgust": "厌恶",
            "surprise": "惊讶"
        }

        # 种族翻译字典
        race_translations = {
            "asian": "亚洲人", "white": "白人", "black": "黑人",
            "middle eastern": "中东人", "latino hispanic": "拉丁裔",
            "indian": "印度人"
        }

        for idx, face in enumerate(analysis):
            region = face.get('region', {})
            x, y, w, h = region.get('x', 0), region.get('y', 0), region.get('w', 0), region.get('h', 0)

            # 判断性别差异，决定框的颜色
            gender_dict = face.get('gender', {})
            male_prob = gender_dict.get('Man', 0)
            female_prob = gender_dict.get('Woman', 0)

            # 如果性别差异小于20%，使用红色框
            if abs(male_prob - female_prob) <= 20:
                color = (255, 0, 0)  # 红色
            else:
                color = (0, 255, 0)  # 绿色

            # 绘制人脸框和序号
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"#{idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # 填充表格
            # 序号
            self.result_table.setItem(idx, 0, QTableWidgetItem(f"#{idx + 1}"))

            # 性别
            if self.detection_options['性别检测']:
                if abs(male_prob - female_prob) <= 20:
                    gender_text = f"未知 (男:{male_prob:.1f}% 女:{female_prob:.1f}%)"
                else:
                    gender_text = "男性" if male_prob > female_prob else "女性"
                self.result_table.setItem(idx, 1, QTableWidgetItem(gender_text))

            # 年龄
            if self.detection_options['年龄检测']:
                self.result_table.setItem(idx, 2, QTableWidgetItem(str(face.get('age', '未知'))))

            # 情绪
            if self.detection_options['情绪检测']:
                emotion = face.get('dominant_emotion', '').lower()
                emotion_cn = emotion_translations.get(emotion, emotion)
                self.result_table.setItem(idx, 3, QTableWidgetItem(emotion_cn))

            # 种族
            if self.detection_options['种族检测']:
                race = face.get('dominant_race', '').lower()
                race_cn = race_translations.get(race, race)
                self.result_table.setItem(idx, 4, QTableWidgetItem(race_cn))

        # 将图片转换为Qt图像并显示
        qt_image = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(self.image_label.size(), Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.current_image = pixmap

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(value)

    def hide_progress(self):
        """隐藏进度条"""
        QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))

    def show_error(self, message):
        """显示错误信息"""
        QMessageBox.warning(self, "错误", message)
        self.progress_bar.setVisible(False)

    def load_image(self):
        """加载图片并进行检测"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.jpg *.jpeg *.png)")
            if not file_path:
                return

            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # 在新线程中处理图片
            def process_image():
                try:
                    # 读取图片
                    self.progress_signal.progress.emit(20)
                    frame = cv2.imread(file_path)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # 获取启用的检测选项
                    actions = [self.option_mapping[option] for option, enabled in
                               self.detection_options.items() if enabled]

                    if not actions:
                        self.progress_signal.error.emit("请至少选择一种检测选项")
                        return

                    self.progress_signal.progress.emit(40)

                    # 分析图片
                    analysis = DeepFace.analyze(
                        img_path=file_path,
                        actions=actions,
                        enforce_detection=False
                    )

                    self.progress_signal.progress.emit(80)

                    # 在主线程中更新UI
                    self.process_face_analysis(frame, analysis)
                    self.progress_signal.progress.emit(100)
                    self.progress_signal.finished.emit()

                except Exception as e:
                    self.progress_signal.error.emit(str(e))

            # 启动处理线程
            threading.Thread(target=process_image, daemon=True).start()

        except Exception as e:
            self.progress_signal.error.emit(str(e))

    def update_frame(self):
        """实时更新摄像头画面并分析"""
        try:
            ret, frame = self.cap.read()
            if not ret:
                raise IOError("无法读取摄像头帧")

            # 转换为RGB格式
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 获取启用的检测选项（转换为英文）
            actions = [self.option_mapping[option] for option, enabled in self.detection_options.items() if enabled]

            if not actions:
                QMessageBox.warning(self, "警告", "请至少选择一种检测选项")
                return

            # 分析摄像头画面
            analysis = DeepFace.analyze(
                img_path=rgb_frame,
                actions=actions,
                enforce_detection=False
            )

            self.process_face_analysis(frame, analysis)

        except Exception as e:
            print(f"实时分析出错: {str(e)}")

    def show_large_image(self, event):
        """查看大图"""
        if self.current_image is not None:
            # 显示尺寸设置对话框
            size_dialog = ImageSizeDialog(self, self.view_width, self.view_height)
            if size_dialog.exec_() == QDialog.Accepted:
                self.view_width, self.view_height = size_dialog.get_size()
                # 保存设置
                self.config.set('view_width', self.view_width)
                self.config.set('view_height', self.view_height)

            # 显示大图对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("查看大图")
            dialog.setFixedSize(self.view_width, self.view_height)
            layout = QVBoxLayout(dialog)

            # 创建工具栏
            toolbar = QHBoxLayout()
            size_button = QPushButton("调整尺寸", dialog)
            size_button.clicked.connect(lambda: self.adjust_image_size(dialog, label))
            toolbar.addWidget(size_button)
            layout.addLayout(toolbar)

            # 显示图片
            label = QLabel(dialog)
            label.setAlignment(Qt.AlignCenter)
            label.setPixmap(self.current_image.scaled(
                self.view_width - 40,  # 考虑边距
                self.view_height - 80,  # 考虑边距和工具栏
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            layout.addWidget(label)

            dialog.exec_()
    def adjust_image_size(self, dialog, image_label):
        """调整图片查看尺寸"""
        size_dialog = ImageSizeDialog(self, self.view_width, self.view_height)
        if size_dialog.exec_() == QDialog.Accepted:
            self.view_width, self.view_height = size_dialog.get_size()
            # 更新对话框和图片尺寸
            dialog.setFixedSize(self.view_width, self.view_height)
            image_label.setPixmap(self.current_image.scaled(
                self.view_width - 40,
                self.view_height - 80,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            # 保存设置
            self.config.set('view_width', self.view_width)
            self.config.set('view_height', self.view_height)

    def closeEvent(self, event):
        """释放资源"""
        if self.cap is not None:
            self.cap.release()
        self.timer.stop()
        self.config.save()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = FaceAnalysisApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()