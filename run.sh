#!/bin/bash -i

APP_HOME="$(dirname "$(realpath "$0")")"

echo "============================="
echo "ADBFileExplorer: ${APP_HOME}"

export PYTHONUNBUFFERED=1
export QT_QPA_PLATFORM=xcb
source $APP_HOME/.venv/bin/activate
python $APP_HOME/src/main.py 2>&1 | tee -a $APP_HOME/output.log
