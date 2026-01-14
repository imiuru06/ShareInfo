# Usage Guide

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Sender (Encrypt)
```bash
python apps/encrypt_app.py
```

1. Enter the data to encrypt.
2. Click **Encrypt**.
3. Copy the **Encrypted Data**.
4. Either:
   - Copy the **Encryption Key** and share it over a separate channel, or
   - Enter a passphrase and copy the **Key Package** JSON.
5. Share the **Key Fingerprint** out-of-band for verification.

## Receiver (Decrypt)
```bash
python apps/decrypt_app.py
```

1. Paste the **Encrypted Data**.
2. Paste the **Encryption Key**, or paste the **Key Package** JSON + passphrase and click **Load Key from Package**.
3. Click **Decrypt**.
4. Compare the **Key Fingerprint** with the sender to confirm integrity.
