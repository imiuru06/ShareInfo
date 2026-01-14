# Usage Guide

## Setup
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

If you already have `uv` installed (e.g., via `brew` or `pipx`), you can skip the install step.

## Packaging (PyInstaller)
```bash
uv pip install -r requirements-dev.txt
pyinstaller --onefile --windowed apps/encrypt_app.py
pyinstaller --onefile --windowed apps/decrypt_app.py
```

The binaries will be placed in the `dist/` directory. For regular usage, run the packaged binaries instead of `python apps/*.py`.

## Distribution Notes
- Build on the target OS (Windows/macOS/Linux) to avoid runtime compatibility issues.
- Verify license compliance for bundled dependencies (PyQt5, cryptography, pyperclip).
- Test the packaged binaries on a clean machine to catch missing DLLs or runtime hooks.
- Keep your signing/notarization workflow ready if distributing to end users (especially macOS/Windows).
- Treat logs as sensitive; the apps write `encrypt_app.log` / `decrypt_app.log` to the working directory.

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

### File Encryption
1. Click **Select File** and choose a file to encrypt.
2. Click **Encrypt File** and save the `.fernet` output (a key will be generated if one does not exist).

## Receiver (Decrypt)
```bash
python apps/decrypt_app.py
```

1. Paste the **Encrypted Data**.
2. Paste the **Encryption Key**, or paste the **Key Package** JSON + passphrase and click **Load Key from Package**.
3. Click **Decrypt**.
4. Compare the **Key Fingerprint** with the sender to confirm integrity.

### File Decryption
1. Click **Select Encrypted File** and choose the `.fernet` file.
2. Provide the key (or load it from a key package).
3. Click **Decrypt File** and save the output file.
