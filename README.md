# ShareInfo

A simple GUI tool for encrypting and decrypting text using Fernet, with a sender and receiver workflow.

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Sender (Encrypt)
```bash
python apps/encrypt_app.py
```

### Receiver (Decrypt)
```bash
python apps/decrypt_app.py
```

### File Support
The GUI supports encrypting files to `.fernet` and decrypting them back on the receiver side.

## Documentation
- [Usage Guide](docs/USAGE.md)
- [Security Guidance](docs/SECURITY.md)
- [Architecture](docs/ARCHITECTURE.md)
