import cv2
import os
import time
from concurrent.futures import Future, ThreadPoolExecutor
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap
try:
    from PySide6.QtMultimedia import QMediaDevices
except Exception:
    QMediaDevices = None
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from ultralytics import YOLO


class MainWindow(QMainWindow):
    _IDLE_PREVIEW_TEXT = (
        '<div style="text-align: center;">'
        '<div style="font-size: 16px; font-weight: 600; color: #4a4a4a;">No source active</div>'
        '<div style="font-size: 13px; color: #6b6f76;">Click Start Source to begin detection</div>'
        "</div>"
    )
    _FEED_IDLE_STYLE = """
        QLabel {
            border: none;
            border-radius: 6px;
            background-color: #f7f8fa;
            color: #666666;
            padding: 0px;
        }
    """
    _FEED_ACTIVE_STYLE = """
        QLabel {
            border: 1px solid #c9c9c9;
            border-radius: 8px;
            background-color: #111111;
            color: #666666;
            font-size: 16px;
            padding: 0px;
        }
    """

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
        root_layout.setSpacing(8)

        source_row = QHBoxLayout()
        source_row.setSpacing(8)
        source_label = QLabel("Source")
        self.source_selector = QComboBox()
        self.source_selector.addItem("Webcam", "webcam")
        self.source_selector.addItem("Video File", "video")
        self.source_selector.currentIndexChanged.connect(self._on_source_changed)
        self.webcam_selector = QComboBox()
        self._populate_webcam_selector()
        self.webcam_selector.currentIndexChanged.connect(self._on_source_changed)
        self.select_file_button = QPushButton("Choose File")
        self.select_file_button.clicked.connect(self.select_source_file)
        self.selected_file_label = QLabel("Using default webcam")
        self.selected_file_label.setStyleSheet("color: #666666; font-size: 12px;")
        source_row.addWidget(source_label)
        source_row.addWidget(self.source_selector)
        source_row.addWidget(self.webcam_selector)
        source_row.addWidget(self.select_file_button)
        source_row.addWidget(self.selected_file_label, stretch=1)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)

        self.start_button = QPushButton("Start Source")
        self.stop_button = QPushButton("Stop Source")
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)

        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)
        self.fps_label = QLabel("FPS: --")
        self.fps_label.setStyleSheet("color: #444444; font-size: 13px;")
        button_row.addWidget(self.fps_label)
        self.status_label = QLabel("Status: Idle")
        self.status_label.setStyleSheet("color: #444444; font-size: 13px;")
        button_row.addWidget(self.status_label)
        button_row.addStretch()

        confidence_row = QHBoxLayout()
        confidence_row.setSpacing(8)
        confidence_label = QLabel("Confidence Threshold")
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(25)
        self.confidence_slider.setSingleStep(1)
        self.confidence_slider.setPageStep(5)
        self.confidence_value_label = QLabel()
        self.confidence_value_label.setMinimumWidth(40)
        self.confidence_value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.confidence_slider.valueChanged.connect(self._update_confidence_label)
        self._update_confidence_label(self.confidence_slider.value())
        confidence_row.addWidget(confidence_label)
        confidence_row.addWidget(self.confidence_slider, stretch=1)
        confidence_row.addWidget(self.confidence_value_label)

        self.model_status = QLabel(model_status_text)
        self.model_status.setWordWrap(True)
        self.model_status.setStyleSheet("color: #444444; font-size: 13px;")

        self.feed_placeholder = QLabel("Source preview will appear here")
        self.feed_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feed_placeholder.setMinimumHeight(240)
        self.feed_placeholder.setMinimumSize(0, 0)
        self.feed_placeholder.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored
        )
        self.feed_placeholder.setStyleSheet(self._FEED_IDLE_STYLE)
        self.feed_placeholder.setText(self._IDLE_PREVIEW_TEXT)

        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet(
            "QFrame { border: 1px solid #d8dde3; border-radius: 10px; background-color: #fbfcfd; }"
        )
        self.preview_frame.setMinimumSize(640, 360)
        self.preview_frame.setMaximumSize(960, 540)
        self.preview_frame.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        preview_layout = QVBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(6, 6, 6, 6)
        preview_layout.setSpacing(0)
        preview_layout.addWidget(self.feed_placeholder)

        source_section = QWidget()
        source_layout = QVBoxLayout(source_section)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(2)
        source_header = QLabel("Source")
        source_header.setStyleSheet("color: #555555; font-size: 11px; font-weight: 600;")
        source_layout.addWidget(source_header)
        source_layout.addLayout(source_row)

        controls_section = QWidget()
        controls_layout = QVBoxLayout(controls_section)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(2)
        controls_header = QLabel("Controls")
        controls_header.setStyleSheet("color: #555555; font-size: 11px; font-weight: 600;")
        controls_layout.addWidget(controls_header)
        controls_layout.addLayout(button_row)

        detection_section = QWidget()
        detection_layout = QVBoxLayout(detection_section)
        detection_layout.setContentsMargins(0, 0, 0, 0)
        detection_layout.setSpacing(2)
        detection_header = QLabel("Detection Settings")
        detection_header.setStyleSheet("color: #555555; font-size: 11px; font-weight: 600;")
        detection_layout.addWidget(detection_header)
        detection_layout.addLayout(confidence_row)
        detection_layout.addWidget(self.model_status)

        top_controls = QWidget()
        top_controls_layout = QVBoxLayout(top_controls)
        top_controls_layout.setContentsMargins(0, 0, 0, 0)
        top_controls_layout.setSpacing(6)
        top_controls_layout.addWidget(source_section)
        top_controls_layout.addWidget(controls_section)
        top_controls_layout.addWidget(detection_section)

        root_layout.addWidget(top_controls)
        root_layout.addWidget(
            self.preview_frame, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        root_layout.addStretch(1)

        self.source_file_path: str | None = None
        self.camera: cv2.VideoCapture | None = None
        self.camera_timer = QTimer(self)
        self.camera_timer.setInterval(30)
        self.camera_timer.timeout.connect(self.update_frame)
        self._inference_executor = ThreadPoolExecutor(max_workers=1)
        self._inference_future: Future | None = None
        self._last_detections: list[tuple[int, int, int, int, float, str]] = []
        self._last_frame_ts: float | None = None
        self._fps: float = 0.0
        self._current_preview_pixmap: QPixmap | None = None
        self.state = "idle"  # possible values: "idle", "running", "error"
        self.update_ui_state()
        self._on_source_changed()

    def update_ui_state(self) -> None:
        # Centralized state-driven UI updates for status and Start/Stop controls.
        if self.state == "running":
            self.status_label.setText("Status: Running")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            return

        if self.state == "error":
            self.status_label.setText("Status: Error")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            return

        self.status_label.setText("Status: Idle")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def _update_confidence_label(self, value: int) -> None:
        self.confidence_value_label.setText(f"{value / 100:.2f}")

    def _open_webcam_capture(self, index: int) -> cv2.VideoCapture | None:
        # Prefer DirectShow on Windows to reduce noisy probe warnings from unavailable indices.
        backend = cv2.CAP_DSHOW if os.name == "nt" and hasattr(cv2, "CAP_DSHOW") else cv2.CAP_ANY
        cap = cv2.VideoCapture(index, backend)
        if cap.isOpened():
            return cap
        cap.release()
        return None

    def _friendly_camera_names(self) -> dict[int, str]:
        if QMediaDevices is None:
            return {}
        try:
            devices = QMediaDevices.videoInputs()
        except Exception:
            return {}

        names: dict[int, str] = {}
        for idx, device in enumerate(devices):
            description = device.description().strip()
            if description:
                names[idx] = description
        return names

    def _camera_label(self, camera_index: int, fallback_other_number: int, camera_name: str | None) -> str:
        if camera_index == 0:
            return f"Default Webcam ({camera_name})" if camera_name else "Default Webcam"
        if camera_name:
            return f"Other Camera ({camera_name})"
        return f"Other Camera {fallback_other_number}"

    def _populate_webcam_selector(self) -> None:
        self.webcam_selector.clear()
        found_indices: list[int] = []
        friendly_names = self._friendly_camera_names()
        for idx in range(5):
            cap = self._open_webcam_capture(idx)
            if cap is not None:
                found_indices.append(idx)
                cap.release()

        if not found_indices:
            self.webcam_selector.addItem("No webcams found", -1)
            self.webcam_selector.setEnabled(False)
            return

        other_camera_number = 1
        for idx in found_indices:
            label = self._camera_label(
                camera_index=idx,
                fallback_other_number=other_camera_number,
                camera_name=friendly_names.get(idx),
            )
            self.webcam_selector.addItem(label, idx)
            if idx != 0:
                other_camera_number += 1
        self.webcam_selector.setEnabled(True)

    def _on_source_changed(self) -> None:
        if self.camera_timer.isActive() or (self.camera is not None and self.camera.isOpened()):
            self.stop_camera()

        source_kind = self.source_selector.currentData()
        is_webcam = source_kind == "webcam"
        self.webcam_selector.setVisible(is_webcam)
        self.select_file_button.setVisible(not is_webcam)
        self.select_file_button.setEnabled(not is_webcam)
        if is_webcam:
            if self.webcam_selector.currentData() is None or int(self.webcam_selector.currentData()) < 0:
                self.selected_file_label.setText("No webcam available")
            else:
                self.selected_file_label.setText(f"Using {self.webcam_selector.currentText()}")
        elif self.source_file_path is None:
            self.selected_file_label.setText("No file selected")

    def select_source_file(self) -> None:
        source_kind = self.source_selector.currentData()
        if source_kind == "video":
            file_filter = "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv)"
        else:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select Source File", "", file_filter)
        if not file_path:
            return

        self.source_file_path = file_path
        self.selected_file_label.setText(os.path.basename(file_path))

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

        detections: list[tuple[int, int, int, int, float, str]] = []
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
            detections.append((x1, y1, x2, y2, confidence, label))

        return detections

    def _draw_and_show_frame(
        self,
        frame,
        detections: list[tuple[int, int, int, int, float, str]],
    ) -> None:
        frame_h, frame_w = frame.shape[:2]
        confidence_threshold = self.confidence_slider.value() / 100.0
        for x1, y1, x2, y2, confidence, label in detections:
            if confidence < confidence_threshold:
                continue

            x1 = max(0, min(x1, frame_w - 1))
            y1 = max(0, min(y1, frame_h - 1))
            x2 = max(0, min(x2, frame_w - 1))
            y2 = max(0, min(y2, frame_h - 1))
            if x2 <= x1 or y2 <= y1:
                continue

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 2
            (text_w, text_h), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )
            text_x = min(max(0, x1), max(0, frame_w - text_w - 2))
            if y1 - 8 - text_h >= 0:
                text_y = y1 - 8
            else:
                text_y = min(frame_h - baseline - 2, y1 + text_h + 8)
            text_y = max(text_h + 2, text_y)

            cv2.putText(
                frame,
                label,
                (text_x, text_y),
                font,
                font_scale,
                (0, 255, 0),
                thickness,
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
        self._current_preview_pixmap = QPixmap.fromImage(image.copy())
        self.feed_placeholder.setText("")
        self._update_preview_pixmap()

    def _update_preview_pixmap(self) -> None:
        if self._current_preview_pixmap is None:
            return

        target_size = self.feed_placeholder.contentsRect().size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            return

        scaled_pixmap = self._current_preview_pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.feed_placeholder.setPixmap(scaled_pixmap)

    def start_camera(self) -> None:
        try:
            if self.camera is not None and self.camera.isOpened():
                return

            source_kind = self.source_selector.currentData()
            self.feed_placeholder.setStyleSheet(self._FEED_ACTIVE_STYLE)
            self.fps_label.setText("FPS: --")
            self._last_frame_ts = None
            self._fps = 0.0
            self._last_detections = []

            if source_kind == "webcam":
                webcam_index = int(self.webcam_selector.currentData())
                if webcam_index < 0:
                    self.feed_placeholder.setText("No webcam available")
                    self.feed_placeholder.setPixmap(QPixmap())
                    return

                self.camera = self._open_webcam_capture(webcam_index)
                if self.camera is None:
                    self.feed_placeholder.setText("Unable to open selected webcam")
                    self.feed_placeholder.setPixmap(QPixmap())
                    return

                self.state = "running"
                self.update_ui_state()
                self.source_selector.setEnabled(False)
                self.webcam_selector.setEnabled(False)
                self.select_file_button.setEnabled(False)
                self.camera_timer.start()
                return

            if not self.source_file_path:
                self.feed_placeholder.setText("Select a video file first")
                self.feed_placeholder.setPixmap(QPixmap())
                return

            self.camera = cv2.VideoCapture(self.source_file_path)
            if not self.camera.isOpened():
                self.camera.release()
                self.camera = None
                self.feed_placeholder.setText("Unable to open video file")
                self.feed_placeholder.setPixmap(QPixmap())
                return

            self.state = "running"
            self.update_ui_state()
            self.source_selector.setEnabled(False)
            self.webcam_selector.setEnabled(False)
            self.select_file_button.setEnabled(False)
            self.camera_timer.start()
        except Exception:
            self.state = "error"
            self.update_ui_state()
            raise

    def stop_camera(self) -> None:
        try:
            self.camera_timer.stop()
            if self.camera is not None:
                self.camera.release()
                self.camera = None

            self.state = "idle"
            self.update_ui_state()
            self.source_selector.setEnabled(True)
            self.webcam_selector.setEnabled(True)
            self._on_source_changed()
            self._current_preview_pixmap = None
            self.feed_placeholder.setPixmap(QPixmap())
            self.feed_placeholder.setText(self._IDLE_PREVIEW_TEXT)
            self.feed_placeholder.setStyleSheet(self._FEED_IDLE_STYLE)
            self._last_detections = []
            self._last_frame_ts = None
            self._fps = 0.0
            self.fps_label.setText("FPS: --")
        except Exception:
            self.state = "error"
            self.update_ui_state()
            raise

    def update_frame(self) -> None:
        if self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            self.stop_camera()
            if self.source_selector.currentData() == "video":
                self.feed_placeholder.setText("Video playback finished")
            else:
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

        now = time.perf_counter()
        if self._last_frame_ts is not None:
            dt = now - self._last_frame_ts
            if dt > 0:
                current_fps = 1.0 / dt
                self._fps = current_fps if self._fps == 0.0 else (self._fps * 0.9 + current_fps * 0.1)
                self.fps_label.setText(f"FPS: {self._fps:.1f}")
        self._last_frame_ts = now

        self._draw_and_show_frame(frame, self._last_detections)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.stop_camera()
        self._inference_executor.shutdown(wait=False, cancel_futures=True)
        super().closeEvent(event)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._update_preview_pixmap()
