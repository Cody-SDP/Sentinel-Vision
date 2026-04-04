import sys

from PySide6.QtWidgets import QApplication

from app.model_loader import load_model
from app.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    model_result = load_model()
    if model_result.loaded:
        model_status_text = f"Model loaded: {model_result.model_path}"
    else:
        model_status_text = (
            f"Model unavailable: {model_result.error or 'Unknown model loading error'}"
        )

    window = MainWindow(model_status_text=model_status_text)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
