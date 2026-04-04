import cv2
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sentinel-Vision")
        self.resize(900, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        self.start_button = QPushButton("Start Camera")
        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)
        button_row.addStretch()

        self.feed_placeholder = QLabel("Webcam feed will appear here")
        self.feed_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feed_placeholder.setMinimumHeight(420)
        self.feed_placeholder.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #c8c8c8;
                border-radius: 10px;
                background-color: #f7f7f7;
                color: #666666;
                font-size: 16px;
            }
            """
        )

        root_layout.addLayout(button_row)
        root_layout.addWidget(self.feed_placeholder, stretch=1)

        self.camera: cv2.VideoCapture | None = None
        self.camera_timer = QTimer(self)
        self.camera_timer.setInterval(30)
        self.camera_timer.timeout.connect(self.update_frame)

    def start_camera(self) -> None:
        if self.camera is not None and self.camera.isOpened():
            return

        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            self.camera.release()
            self.camera = None
            self.feed_placeholder.setText("No webcam available")
            self.feed_placeholder.setPixmap(QPixmap())
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.camera_timer.start()

    def stop_camera(self) -> None:
        self.camera_timer.stop()
        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.feed_placeholder.setPixmap(QPixmap())
        self.feed_placeholder.setText("Webcam feed will appear here")

    def update_frame(self) -> None:
        if self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            self.stop_camera()
            self.feed_placeholder.setText("Unable to read from webcam")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = rgb_frame.shape
        bytes_per_line = channels * width
        image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(image).scaled(
            self.feed_placeholder.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.feed_placeholder.setText("")
        self.feed_placeholder.setPixmap(pixmap)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.stop_camera()
        super().closeEvent(event)
