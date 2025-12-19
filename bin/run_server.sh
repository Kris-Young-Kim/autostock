#!/bin/bash
# Flask 서버 실행 스크립트
# US Market Alpha Platform Web Server

cd "$(dirname "$0")/.."

echo "🚀 Starting Flask server..."
echo "📁 Working directory: $(pwd)"

# Python 가상환경 활성화 (있는 경우)
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🔧 Activating virtual environment..."
    source .venv/bin/activate
fi

# 서버 실행
python web/app.py

