from PySide6.QtCore import Qt
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
