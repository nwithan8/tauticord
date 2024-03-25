#!/bin/bash

MIGRATION_NUMBER="001"
MIGRATION_PYTHON_SCRIPT="001_env_var_to_config_yaml.py"
MIGRATIONS_FOLDER="/app/migrations"
MODULES_FOLDER="/app/modules"
MIGRATION_TRACKER="/config/.migrations"
CONFIG_FOLDER="/config"
LOGS_FOLDER="/logs"

TMP_MIGRATION_FOLDER="tmp_migration_001_env_var_to_config_yaml"

# Create a .migration file if it doesn't exist
touch "$MIGRATION_TRACKER"

# Make temporary directory for migration process
mkdir -p "$TMP_MIGRATION_FOLDER"

# Copy "migrations" and "modules" directories to the temporary directory (needed for migration scripts to access modules)
cp -r "$MIGRATIONS_FOLDER" "$TMP_MIGRATION_FOLDER/migrations"
cp -r "$MODULES_FOLDER" "$TMP_MIGRATION_FOLDER/modules"

# Enter the temporary directory
cd "$TMP_MIGRATION_FOLDER" || exit

# Run the migration Python script
echo "Running migration $MIGRATION_NUMBER"
/app/venv/bin/python3 "migrations/$MIGRATION_PYTHON_SCRIPT" "$MIGRATION_TRACKER" "$CONFIG_FOLDER" "$LOGS_FOLDER"

# Remove the temporary directory
cd ..
rm -r "$TMP_MIGRATION_FOLDER"
