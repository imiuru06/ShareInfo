# ShareInfo

A simple GUI tool for encrypting and decrypting text using Fernet, with a sender and receiver workflow.

## Quick Start
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

If you already have `uv` installed (e.g., via `brew` or `pipx`), you can skip the install step.

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
uv pip install -r requirements-dev.txt
pyinstaller --onefile --windowed apps/encrypt_app.py
pyinstaller --onefile --windowed apps/decrypt_app.py
```

Use the generated binaries from `dist/` for real-world usage instead of running the Python scripts directly.

### Packaging Checklist (Before Distribution)
- Build on the target OS/architecture to avoid runtime incompatibilities.
- Validate that Qt plugins and cryptography dependencies load on a clean machine.
- Treat `encrypt_app.log` / `decrypt_app.log` as sensitive artifacts; avoid shipping logs in public builds.
- Keep signing/notarization and dependency license checks in your release process.
- If you need to bundle extra assets, ensure `--add-data` paths are correct for your OS.

### Distribution-Ready Commands
Build from the repository root to ensure local modules are discovered.

**One-file builds (single executable)**
```bash
uv pip install -r requirements-dev.txt
pyinstaller --paths . --collect-submodules src --onefile --windowed --name encrypt_app apps/encrypt_app.py
pyinstaller --paths . --collect-submodules src --onefile --windowed --name decrypt_app apps/decrypt_app.py
```

**Spec-driven builds (repeatable releases)**
```bash
pyinstaller --paths . --collect-submodules src --onefile --windowed --name encrypt_app --specpath build/spec apps/encrypt_app.py
pyinstaller --paths . --collect-submodules src --onefile --windowed --name decrypt_app --specpath build/spec apps/decrypt_app.py
```
Edit the generated `build/spec/*.spec` files to add resources under `datas` and custom search paths under `pathex`.

**Adding assets**
- Windows: `--add-data "path\\to\\asset;dest"`
- macOS/Linux: `--add-data "path/to/asset:dest"`

If you need to ship assets (icons/configs/templates), prefer adding them to the `.spec` file so every build uses the same mapping.

## Documentation
- [Usage Guide](docs/USAGE.md)
- [Security Guidance](docs/SECURITY.md)
- [Architecture](docs/ARCHITECTURE.md)
