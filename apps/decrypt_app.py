import json
import logging
import sys
from pathlib import Path

import pyperclip
from pyperclip import PyperclipException
from PyQt5.QtCore import QStandardPaths, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

def _add_runtime_paths() -> None:
    if getattr(sys, "frozen", False):
        bundle_root = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
        exec_root = Path(sys.executable).resolve().parent
        candidates = [
            bundle_root,
            bundle_root / "src",
            exec_root,
            exec_root / "src",
        ]
    else:
        repo_root = Path(__file__).resolve().parents[1]
        candidates = [
            repo_root,
            repo_root / "src",
        ]

    for candidate in candidates:
        if candidate.exists():
            sys.path.insert(0, str(candidate))


_add_runtime_paths()

from src.crypto_utils import (
    KeyPackage,
    decrypt_bytes,
    decrypt_text,
    key_fingerprint,
    unwrap_key_with_passphrase,
)

def _log_directory() -> Path:
    if getattr(sys, "frozen", False):
        base_dir = Path(sys.executable).resolve().parent
    else:
        app_data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        base_dir = Path(app_data) if app_data else Path.home() / ".shareinfo"
    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


LOG_PATH = _log_directory() / "decrypt_app.log"
try:
    LOG_PATH.touch(exist_ok=True)
except OSError as exc:  # pragma: no cover - best effort
    print(f"Failed to create log file at {LOG_PATH}: {exc}", file=sys.stderr)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class DecryptApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.key: bytes | None = None
        self.decrypted_text: str | None = None
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("Data Decryption")

        self.encrypted_label = QLabel("Encrypted Data:")
        self.encrypted_text = QTextEdit()

        self.key_label = QLabel("Encryption Key (paste or load from package):")
        self.key_entry = QLineEdit()

        self.key_package_label = QLabel("Key Package (JSON):")
        self.key_package_text = QTextEdit()

        self.passphrase_label = QLabel("Passphrase (for key package):")
        self.passphrase_entry = QLineEdit()
        self.passphrase_entry.setEchoMode(QLineEdit.Password)

        self.load_key_button = QPushButton("Load Key from Package")
        self.load_key_button.clicked.connect(self.load_key_from_package)

        self.fingerprint_label = QLabel("Key Fingerprint:")
        self.fingerprint_value = QLineEdit()
        self.fingerprint_value.setReadOnly(True)

        self.decrypt_button = QPushButton("Decrypt")
        self.decrypt_button.clicked.connect(self.decrypt_data)

        self.decrypted_label = QLabel("Decrypted Data:")
        self.decrypted_text = QTextEdit()
        self.decrypted_text.setReadOnly(True)

        self.copy_button = QPushButton("Copy Decrypted Data")
        self.copy_button.clicked.connect(self.copy_decrypted_data)

        self.file_label = QLabel("File Decryption:")
        self.file_path_entry = QLineEdit()
        self.file_path_entry.setReadOnly(True)
        self.file_select_button = QPushButton("Select Encrypted File")
        self.file_select_button.clicked.connect(self.select_file)
        self.decrypt_file_button = QPushButton("Decrypt File")
        self.decrypt_file_button.clicked.connect(self.decrypt_file)

        self.log_button = QPushButton("Open Log Folder")
        self.log_button.clicked.connect(self.open_log_folder)

        layout = QVBoxLayout()
        layout.addWidget(self.encrypted_label)
        layout.addWidget(self.encrypted_text)
        layout.addWidget(self.key_label)
        layout.addWidget(self.key_entry)
        layout.addWidget(self.key_package_label)
        layout.addWidget(self.key_package_text)
        layout.addWidget(self.passphrase_label)
        layout.addWidget(self.passphrase_entry)
        layout.addWidget(self.load_key_button)
        layout.addWidget(self.fingerprint_label)
        layout.addWidget(self.fingerprint_value)
        layout.addWidget(self.decrypt_button)
        layout.addWidget(self.decrypted_label)
        layout.addWidget(self.decrypted_text)
        layout.addWidget(self.copy_button)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_path_entry)
        layout.addWidget(self.file_select_button)
        layout.addWidget(self.decrypt_file_button)
        layout.addWidget(self.log_button)

        self.setLayout(layout)

    def load_key_from_package(self) -> None:
        raw_package = self.key_package_text.toPlainText().strip()
        passphrase = self.passphrase_entry.text().strip()
        if not raw_package:
            QMessageBox.critical(self, "Error", "Please paste a key package first.")
            logging.error("No key package provided.")
            return
        if not passphrase:
            QMessageBox.critical(self, "Error", "Please enter the passphrase for the key package.")
            logging.error("No passphrase provided for key package.")
            return

        try:
            key_package = KeyPackage.from_json(raw_package)
            self.key = unwrap_key_with_passphrase(key_package, passphrase)
            self.key_entry.setText(self.key.decode())
            self.fingerprint_value.setText(key_fingerprint(self.key))
            QMessageBox.information(self, "Loaded", "Key loaded from package successfully.")
            logging.info("Key loaded from package.")
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            QMessageBox.critical(self, "Error", f"Invalid key package: {exc}")
            logging.error("Invalid key package: %s", exc)
        except Exception as exc:  # pragma: no cover - GUI safety net
            QMessageBox.critical(self, "Error", f"Failed to load key: {exc}")
            logging.error("Failed to load key: %s", exc)

    def decrypt_data(self) -> None:
        encrypted_data = self.encrypted_text.toPlainText().strip()
        if not encrypted_data:
            QMessageBox.critical(self, "Error", "Please enter encrypted data to decrypt.")
            logging.error("No encrypted data provided for decryption.")
            return

        raw_key = self.key_entry.text().strip()
        if not raw_key:
            QMessageBox.critical(self, "Error", "Please provide the encryption key or load it from a package.")
            logging.error("No key provided for decryption.")
            return

        try:
            self.key = raw_key.encode()
            self.decrypted_text = decrypt_text(encrypted_data, self.key)
            self.decrypted_text_widget_set(self.decrypted_text)
            self.fingerprint_value.setText(key_fingerprint(self.key))
            QMessageBox.information(self, "Success", "Data decrypted successfully.")
            logging.info("Data decrypted successfully.")
        except Exception as exc:  # pragma: no cover - GUI safety net
            QMessageBox.critical(self, "Error", f"Decryption failed: {exc}")
            logging.error("Decryption failed: %s", exc)

    def decrypted_text_widget_set(self, text: str) -> None:
        self.decrypted_text.setText(text)

    def copy_decrypted_data(self) -> None:
        if self.decrypted_text:
            try:
                pyperclip.copy(self.decrypted_text)
                QMessageBox.information(self, "Copied", "Decrypted data copied to clipboard.")
                logging.info("Decrypted data copied to clipboard.")
            except PyperclipException as exc:
                QMessageBox.critical(self, "Error", f"Clipboard unavailable: {exc}")
                logging.error("Clipboard unavailable: %s", exc)
        else:
            QMessageBox.critical(self, "Error", "No decrypted data to copy.")
            logging.error("No decrypted data to copy.")

    def select_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Encrypted File", "", "Encrypted Files (*.fernet);;All Files (*)")
        if file_path:
            self.file_path_entry.setText(file_path)

    def decrypt_file(self) -> None:
        file_path = self.file_path_entry.text().strip()
        if not file_path:
            QMessageBox.critical(self, "Error", "Please select an encrypted file.")
            logging.error("No encrypted file selected for decryption.")
            return

        raw_key = self.key_entry.text().strip()
        if not raw_key:
            QMessageBox.critical(self, "Error", "Please provide the encryption key or load it from a package.")
            logging.error("No key provided for file decryption.")
            return

        try:
            self.key = raw_key.encode()
            with open(file_path, "rb") as file_handle:
                encrypted_payload = file_handle.read()
            decrypted_payload = decrypt_bytes(encrypted_payload, self.key)
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted File")
            if not save_path:
                logging.info("File decryption canceled (no save path selected).")
                return
            with open(save_path, "wb") as file_handle:
                file_handle.write(decrypted_payload)
            self.fingerprint_value.setText(key_fingerprint(self.key))
            QMessageBox.information(self, "Success", "File decrypted and saved successfully.")
            logging.info("File decrypted successfully: %s", save_path)
        except Exception as exc:  # pragma: no cover - GUI safety net
            QMessageBox.critical(self, "Error", f"File decryption failed: {exc}")
            logging.error("File decryption failed: %s", exc)

    def open_log_folder(self) -> None:
        url = QUrl.fromLocalFile(str(_log_directory()))
        if not QDesktopServices.openUrl(url):
            QMessageBox.critical(self, "Error", "Failed to open log folder.")
            logging.error("Failed to open log folder: %s", LOG_PATH)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ex = DecryptApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as exc:  # pragma: no cover - GUI safety net
        logging.critical("Unhandled exception: %s", exc)
        QMessageBox.critical(None, "Critical Error", f"Unhandled exception: {exc}")
