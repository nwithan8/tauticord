UNIX_BIN = .venv/bin
WINDOWS_BIN = .venv\Scripts

install-unix:
	${UNIX_BIN}/pip install -r requirements.txt

install-win:
	${WINDOWS_BIN}\pip.exe install -r .\requirements.txt

validate-example-config-unix:
	${UNIX_BIN}/python ci/validate_example_config.py .schema/config_v2.schema.json tauticord.yaml.example

validate-example-config-win:
	${WINDOWS_BIN}\python.exe ci\validate_example_config.py .schema\config_v2.schema.json tauticord.yaml.example
