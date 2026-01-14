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

from app_crypto_utils import (
    encrypt_bytes,
    encrypt_text,
    generate_key,
    key_fingerprint,
    wrap_key_with_passphrase,
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


LOG_PATH = _log_directory() / "encrypt_app.log"
try:
    LOG_PATH.touch(exist_ok=True)
except OSError as exc:  # pragma: no cover - best effort
    print(f"Failed to create log file at {LOG_PATH}: {exc}", file=sys.stderr)

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class EncryptApp(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.key: bytes | None = None
        self.encrypted_data: str | None = None
        self.key_package_json: str | None = None
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle("Data Encryption")

        self.label = QLabel("Enter the data to encrypt:")
        self.text_edit = QTextEdit()

        self.encrypt_button = QPushButton("Encrypt")
        self.encrypt_button.clicked.connect(self.encrypt_data)

        self.key_label = QLabel("Encryption Key (share separately):")
        self.key_entry = QLineEdit()
        self.key_entry.setReadOnly(True)

        self.key_fingerprint_label = QLabel("Key Fingerprint:")
        self.key_fingerprint_value = QLineEdit()
        self.key_fingerprint_value.setReadOnly(True)

        self.copy_key_button = QPushButton("Copy Key to Clipboard")
        self.copy_key_button.clicked.connect(self.copy_key)

        self.passphrase_label = QLabel("Optional Passphrase (protects key package):")
        self.passphrase_entry = QLineEdit()
        self.passphrase_entry.setEchoMode(QLineEdit.Password)
        self.passphrase_entry.textChanged.connect(self._update_key_package)

        self.key_package_label = QLabel("Key Package (JSON for passphrase unlock):")
        self.key_package_text = QTextEdit()
        self.key_package_text.setReadOnly(True)

        self.copy_key_package_button = QPushButton("Copy Key Package")
        self.copy_key_package_button.clicked.connect(self.copy_key_package)

        self.encrypted_data_label = QLabel("Encrypted Data:")
        self.encrypted_data_text = QTextEdit()
        self.encrypted_data_text.setReadOnly(True)

        self.copy_data_button = QPushButton("Copy Data to Clipboard")
        self.copy_data_button.clicked.connect(self.copy_data)

        self.file_label = QLabel("File Encryption:")
        self.file_path_entry = QLineEdit()
        self.file_path_entry.setReadOnly(True)
        self.file_select_button = QPushButton("Select File")
        self.file_select_button.clicked.connect(self.select_file)
        self.encrypt_file_button = QPushButton("Encrypt File")
        self.encrypt_file_button.clicked.connect(self.encrypt_file)

        self.log_button = QPushButton("Open Log Folder")
        self.log_button.clicked.connect(self.open_log_folder)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.encrypt_button)
        layout.addWidget(self.key_label)
        layout.addWidget(self.key_entry)
        layout.addWidget(self.key_fingerprint_label)
        layout.addWidget(self.key_fingerprint_value)
        layout.addWidget(self.copy_key_button)
        layout.addWidget(self.passphrase_label)
        layout.addWidget(self.passphrase_entry)
        layout.addWidget(self.key_package_label)
        layout.addWidget(self.key_package_text)
        layout.addWidget(self.copy_key_package_button)
        layout.addWidget(self.encrypted_data_label)
        layout.addWidget(self.encrypted_data_text)
        layout.addWidget(self.copy_data_button)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_path_entry)
        layout.addWidget(self.file_select_button)
        layout.addWidget(self.encrypt_file_button)
        layout.addWidget(self.log_button)

        self.setLayout(layout)

    def encrypt_data(self) -> None:
        data = self.text_edit.toPlainText().strip()
        if not data:
            QMessageBox.critical(self, "Error", "Please enter some data to encrypt.")
            logging.error("No data entered for encryption.")
            return

        try:
            self.key = generate_key()
            self.encrypted_data = encrypt_text(data, self.key)
            self.key_entry.setText(self.key.decode())
            self.key_fingerprint_value.setText(key_fingerprint(self.key))
            self.encrypted_data_text.setText(self.encrypted_data)

            self._update_key_package()

            QMessageBox.information(
                self,
                "Success",
                "Data encrypted successfully. Share the key separately or use the key package with a passphrase.",
            )
            logging.info("Data encrypted successfully.")
        except Exception as exc:  # pragma: no cover - GUI safety net
            QMessageBox.critical(self, "Error", f"Encryption failed: {exc}")
            logging.error("Encryption failed: %s", exc)

    def copy_key(self) -> None:
        if self.key:
            try:
                pyperclip.copy(self.key.decode())
                QMessageBox.information(self, "Copied", "Encryption key copied to clipboard.")
                logging.info("Encryption key copied to clipboard.")
            except PyperclipException as exc:
                QMessageBox.critical(self, "Error", f"Clipboard unavailable: {exc}")
                logging.error("Clipboard unavailable: %s", exc)
        else:
            QMessageBox.critical(self, "Error", "No encryption key to copy.")
            logging.error("No encryption key to copy.")

    def copy_key_package(self) -> None:
        if self.key_package_json:
            try:
                pyperclip.copy(self.key_package_json)
                QMessageBox.information(self, "Copied", "Key package copied to clipboard.")
                logging.info("Key package copied to clipboard.")
            except PyperclipException as exc:
                QMessageBox.critical(self, "Error", f"Clipboard unavailable: {exc}")
                logging.error("Clipboard unavailable: %s", exc)
        else:
            QMessageBox.critical(self, "Error", "No key package to copy.")
            logging.error("No key package to copy.")

    def copy_data(self) -> None:
        if self.encrypted_data:
            try:
                pyperclip.copy(self.encrypted_data)
                QMessageBox.information(self, "Copied", "Encrypted data copied to clipboard.")
                logging.info("Encrypted data copied to clipboard.")
            except PyperclipException as exc:
                QMessageBox.critical(self, "Error", f"Clipboard unavailable: {exc}")
                logging.error("Clipboard unavailable: %s", exc)
        else:
            QMessageBox.critical(self, "Error", "No encrypted data to copy.")
            logging.error("No encrypted data to copy.")

    def _update_key_package(self) -> None:
        passphrase = self.passphrase_entry.text().strip()
        if passphrase and self.key:
            key_package = wrap_key_with_passphrase(self.key, passphrase)
            self.key_package_json = key_package.to_json()
            self.key_package_text.setText(self.key_package_json)
        else:
            self.key_package_json = None
            self.key_package_text.clear()

    def select_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Encrypt")
        if file_path:
            self.file_path_entry.setText(file_path)

    def encrypt_file(self) -> None:
        file_path = self.file_path_entry.text().strip()
        if not file_path:
            QMessageBox.critical(self, "Error", "Please select a file to encrypt.")
            logging.error("No file selected for encryption.")
            return

        try:
            if not self.key:
                self.key = generate_key()
                self.key_entry.setText(self.key.decode())
                self.key_fingerprint_value.setText(key_fingerprint(self.key))
                self._update_key_package()
            with open(file_path, "rb") as file_handle:
                payload = file_handle.read()
            encrypted_payload = encrypt_bytes(payload, self.key)
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Encrypted File",
                f"{file_path}.fernet",
                "Encrypted Files (*.fernet);;All Files (*)",
            )
            if not save_path:
                logging.info("File encryption canceled (no save path selected).")
                return
            with open(save_path, "wb") as file_handle:
                file_handle.write(encrypted_payload)
            QMessageBox.information(self, "Success", "File encrypted and saved successfully.")
            logging.info("File encrypted successfully: %s", save_path)
        except Exception as exc:  # pragma: no cover - GUI safety net
            QMessageBox.critical(self, "Error", f"File encryption failed: {exc}")
            logging.error("File encryption failed: %s", exc)

    def open_log_folder(self) -> None:
        url = QUrl.fromLocalFile(str(_log_directory()))
        if not QDesktopServices.openUrl(url):
            QMessageBox.critical(self, "Error", "Failed to open log folder.")
            logging.error("Failed to open log folder: %s", LOG_PATH)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ex = EncryptApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as exc:  # pragma: no cover - GUI safety net
        logging.critical("Unhandled exception: %s", exc)
        QMessageBox.critical(None, "Critical Error", f"Unhandled exception: {exc}")
