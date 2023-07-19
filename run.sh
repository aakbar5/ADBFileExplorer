#!/bin/bash -i

APP_HOME="$(dirname "$(realpath "$0")")"

echo "============================="
echo "ADBFileExplorer: ${APP_HOME}"

export PYTHONUNBUFFERED=1
source $APP_HOME/.venv/bin/activate
python $APP_HOME/src/main.py
