import cv2
from concurrent.futures import Future, ThreadPoolExecutor
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
from ultralytics import YOLO


class MainWindow(QMainWindow):
    def __init__(
        self,
        model: YOLO | None = None,
        model_status_text: str = "Model status unknown",
    ) -> None:
        super().__init__()
        self.model = model
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

        self.model_status = QLabel(model_status_text)
        self.model_status.setWordWrap(True)
        self.model_status.setStyleSheet("color: #444444; font-size: 13px;")

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
        root_layout.addWidget(self.model_status)
        root_layout.addWidget(self.feed_placeholder, stretch=1)

        self.camera: cv2.VideoCapture | None = None
        self.camera_timer = QTimer(self)
        self.camera_timer.setInterval(30)
        self.camera_timer.timeout.connect(self.update_frame)
        self._inference_executor = ThreadPoolExecutor(max_workers=1)
        self._inference_future: Future | None = None
        self._last_detections: list[tuple[int, int, int, int, str]] = []

    def _run_inference(self, frame_bgr):
        if self.model is None:
            return []

        frame_h, frame_w = frame_bgr.shape[:2]
        infer_size = 640
        scale = min(infer_size / frame_w, infer_size / frame_h, 1.0)
        if scale < 1.0:
            infer_w = max(1, int(frame_w * scale))
            infer_h = max(1, int(frame_h * scale))
            infer_frame = cv2.resize(
                frame_bgr, (infer_w, infer_h), interpolation=cv2.INTER_LINEAR
            )
        else:
            infer_frame = frame_bgr

        results = self.model.predict(source=infer_frame, verbose=False)
        if not results:
            return []

        result = results[0]
        boxes = result.boxes
        if boxes is None or boxes.xyxy is None:
            return []

        names = result.names or {}
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy() if boxes.conf is not None else []
        classes = boxes.cls.cpu().numpy().astype(int) if boxes.cls is not None else []

        detections: list[tuple[int, int, int, int, str]] = []
        scale_back = 1.0 / scale if scale < 1.0 else 1.0
        for i, box in enumerate(xyxy):
            x1, y1, x2, y2 = box.tolist()
            x1 = int(max(0, x1 * scale_back))
            y1 = int(max(0, y1 * scale_back))
            x2 = int(max(0, x2 * scale_back))
            y2 = int(max(0, y2 * scale_back))
            cls_idx = int(classes[i]) if i < len(classes) else -1
            class_name = names.get(cls_idx, str(cls_idx))
            confidence = float(confs[i]) if i < len(confs) else 0.0
            label = f"{class_name} {confidence:.2f}"
            detections.append((x1, y1, x2, y2, label))

        return detections

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
        self._last_detections = []

    def update_frame(self) -> None:
        if self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            self.stop_camera()
            self.feed_placeholder.setText("Unable to read from webcam")
            return

        if self._inference_future is not None and self._inference_future.done():
            try:
                self._last_detections = self._inference_future.result()
            except Exception:
                self._last_detections = []
            finally:
                self._inference_future = None

        if self.model is not None and self._inference_future is None:
            self._inference_future = self._inference_executor.submit(
                self._run_inference, frame.copy()
            )

        for x1, y1, x2, y2, label in self._last_detections:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

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
        self._inference_executor.shutdown(wait=False, cancel_futures=True)
        super().closeEvent(event)
