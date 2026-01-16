#!/bin/bash

# スクリプトのある場所を基準にパスを解決
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Streamlit アプリのパス（app/main.py）
APP_PATH="$SCRIPT_DIR/app/main.py"

# Streamlit アプリを起動
uv run streamlit run "$APP_PATH" --server.enableCORS=false --server.enableXsrfProtection=false
