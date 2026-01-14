# Architecture Overview

## Components
- **Encrypt GUI** (`apps/encrypt_app.py`): Collects plaintext, encrypts data, and produces ciphertext + key artifacts.
- **Decrypt GUI** (`apps/decrypt_app.py`): Accepts ciphertext and key artifacts to decrypt data.
- **Crypto Utilities** (`src/crypto_utils.py`): Shared logic for encryption, decryption, key packaging, and fingerprints.

## Data Flow
1. Sender encrypts plaintext using a random Fernet key.
2. Sender shares ciphertext with the receiver.
3. Sender shares either the raw key (separate channel) or a passphrase-protected key package.
4. Receiver verifies key fingerprint and decrypts.

## File Flow
1. Sender encrypts a file and saves a `.fernet` output.
2. Sender shares the encrypted file and key (or key package + passphrase) via separate channels.
3. Receiver decrypts the `.fernet` file using the key.
