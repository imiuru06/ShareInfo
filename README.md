# ShareInfo

A simple GUI tool for encrypting and decrypting text using Fernet, with a sender and receiver workflow.

## Quick Start
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
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

### Packaging (Recommended for Daily Use)
```bash
pyinstaller --onefile --windowed apps/encrypt_app.py
pyinstaller --onefile --windowed apps/decrypt_app.py
```

Use the generated binaries from `dist/` for real-world usage instead of running the Python scripts directly.

## Documentation
- [Usage Guide](docs/USAGE.md)
- [Security Guidance](docs/SECURITY.md)
- [Architecture](docs/ARCHITECTURE.md)
