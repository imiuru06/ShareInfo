import base64
import hashlib
import json
import os
from dataclasses import dataclass

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16


@dataclass
class KeyPackage:
    wrapped_key: str
    salt: str
    iterations: int = PBKDF2_ITERATIONS
    kdf: str = "PBKDF2HMAC-SHA256"

    def to_json(self) -> str:
        return json.dumps(
            {
                "wrapped_key": self.wrapped_key,
                "salt": self.salt,
                "iterations": self.iterations,
                "kdf": self.kdf,
            }
        )

    @staticmethod
    def from_json(raw: str) -> "KeyPackage":
        data = json.loads(raw)
        return KeyPackage(
            wrapped_key=data["wrapped_key"],
            salt=data["salt"],
            iterations=int(data.get("iterations", PBKDF2_ITERATIONS)),
            kdf=data.get("kdf", "PBKDF2HMAC-SHA256"),
        )


def generate_key() -> bytes:
    return Fernet.generate_key()


def encrypt_text(plain_text: str, key: bytes) -> str:
    cipher_suite = Fernet(key)
    token = cipher_suite.encrypt(plain_text.encode())
    return token.decode()


def decrypt_text(token: str, key: bytes) -> str:
    cipher_suite = Fernet(key)
    plain_text = cipher_suite.decrypt(token.encode())
    return plain_text.decode()


def key_fingerprint(key: bytes) -> str:
    digest = hashlib.sha256(key).hexdigest()
    return " ".join(digest[i : i + 4] for i in range(0, len(digest), 4))


def wrap_key_with_passphrase(key: bytes, passphrase: str) -> KeyPackage:
    salt = os.urandom(SALT_BYTES)
    derived_key = _derive_key(passphrase, salt)
    wrapper = Fernet(derived_key)
    wrapped_key = wrapper.encrypt(key).decode()
    return KeyPackage(
        wrapped_key=wrapped_key,
        salt=base64.urlsafe_b64encode(salt).decode(),
    )


def unwrap_key_with_passphrase(key_package: KeyPackage, passphrase: str) -> bytes:
    salt = base64.urlsafe_b64decode(key_package.salt.encode())
    derived_key = _derive_key(passphrase, salt, key_package.iterations)
    wrapper = Fernet(derived_key)
    return wrapper.decrypt(key_package.wrapped_key.encode())


def _derive_key(passphrase: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
