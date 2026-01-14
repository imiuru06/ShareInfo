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

### Logs 확인
앱 화면의 **Open Log Folder** 버튼을 누르면 로그가 저장된 폴더가 열립니다.
로그는 PyInstaller 실행 파일과 동일한 폴더의 `logs/`에 저장되며, 소스 실행 시에는 OS별 AppData 위치(예: macOS `~/Library/Application Support/ShareInfo/`, Windows `%APPDATA%\\ShareInfo`) 하위의 `logs/`에 저장됩니다.

### Packaging (Recommended for Daily Use)
```bash
uv pip install -r requirements-dev.txt
pyinstaller --onefile --windowed apps/encrypt_app.py
pyinstaller --onefile --windowed apps/decrypt_app.py
```

Use the generated binaries from `dist/` for real-world usage instead of running the Python scripts directly.

### PyInstaller 오류 해결 (`ModuleNotFoundError: No module named 'src'`)
패키징 후 실행 시 위 오류가 발생하면 다음 순서로 확인하세요.

1. **레포지토리 루트에서 빌드했는지 확인**
   ```bash
   pwd
   # /workspace/ShareInfo 와 같은 프로젝트 루트여야 합니다.
   ```
2. **`src` 경로를 PyInstaller에 명시**
   ```bash
   pyinstaller --onefile --windowed --paths src apps/encrypt_app.py
   pyinstaller --onefile --windowed --paths src apps/decrypt_app.py
   ```
3. **기존 빌드 정리 후 재빌드**
   ```bash
   rm -rf build dist *.spec
   pyinstaller --onefile --windowed --paths src apps/encrypt_app.py
   pyinstaller --onefile --windowed --paths src apps/decrypt_app.py
   ```

위 조치 후에도 문제가 지속되면 `dist/` 바이너리를 실행한 로그(예: 터미널 출력)와 함께 알려주세요.

## Documentation
- [Usage Guide](docs/USAGE.md)
- [Security Guidance](docs/SECURITY.md)
- [Architecture](docs/ARCHITECTURE.md)
