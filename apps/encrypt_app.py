import logging
import sys
from pathlib import Path

import pyperclip
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.crypto_utils import (
    encrypt_text,
    generate_key,
    key_fingerprint,
    wrap_key_with_passphrase,
)

logging.basicConfig(
    filename="encrypt_app.log",
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

            passphrase = self.passphrase_entry.text().strip()
            if passphrase:
                key_package = wrap_key_with_passphrase(self.key, passphrase)
                self.key_package_json = key_package.to_json()
                self.key_package_text.setText(self.key_package_json)
            else:
                self.key_package_json = None
                self.key_package_text.clear()

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
            pyperclip.copy(self.key.decode())
            QMessageBox.information(self, "Copied", "Encryption key copied to clipboard.")
            logging.info("Encryption key copied to clipboard.")
        else:
            QMessageBox.critical(self, "Error", "No encryption key to copy.")
            logging.error("No encryption key to copy.")

    def copy_key_package(self) -> None:
        if self.key_package_json:
            pyperclip.copy(self.key_package_json)
            QMessageBox.information(self, "Copied", "Key package copied to clipboard.")
            logging.info("Key package copied to clipboard.")
        else:
            QMessageBox.critical(self, "Error", "No key package to copy.")
            logging.error("No key package to copy.")

    def copy_data(self) -> None:
        if self.encrypted_data:
            pyperclip.copy(self.encrypted_data)
            QMessageBox.information(self, "Copied", "Encrypted data copied to clipboard.")
            logging.info("Encrypted data copied to clipboard.")
        else:
            QMessageBox.critical(self, "Error", "No encrypted data to copy.")
            logging.error("No encrypted data to copy.")


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        ex = EncryptApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as exc:  # pragma: no cover - GUI safety net
        logging.critical("Unhandled exception: %s", exc)
        QMessageBox.critical(None, "Critical Error", f"Unhandled exception: {exc}")
