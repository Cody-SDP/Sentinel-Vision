import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.model_loader import load_model
from app.ui.main_window import MainWindow


def _resolve_icon_path() -> Path:
    # PyInstaller extracts bundled files to sys._MEIPASS at runtime.
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    icon_path = base_path / "assets" / "Sentinel-Vision-new.ico"
    if icon_path.exists():
        return icon_path
    return Path(__file__).resolve().parents[1] / "assets" / "Sentinel-Vision-new.ico"


def main() -> int:
    app = QApplication(sys.argv)
    icon = QIcon(str(_resolve_icon_path()))
    app.setWindowIcon(icon)

    model_result = load_model()
    if model_result.loaded:
        model_name = os.path.basename(model_result.model_path) if model_result.model_path else "Unknown"
        model_status_text = f"Model loaded: {model_name}"
    else:
        model_status_text = (
            f"Model unavailable: {model_result.error or 'Unknown model loading error'}"
        )

    window = MainWindow(model=model_result.model, model_status_text=model_status_text)
    window.setWindowIcon(icon)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
