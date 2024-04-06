UNIX_BIN = .venv/bin
WINDOWS_BIN = .venv\Scripts

install-unix:
	${UNIX_BIN}/pip install -r requirements.txt

install-win:
	${WINDOWS_BIN}\pip.exe install -r .\requirements.txt