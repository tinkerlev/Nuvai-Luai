#!/bin/bash

echo ""
echo "🚀 Starting Nuvai system (Backend + Frontend)..."
echo ""

# Detect operating system
OS_TYPE="unknown"
TERM_CMD=""
IS_WSL=false

if grep -qi microsoft /proc/version 2>/dev/null; then
    OS_TYPE="wsl"
    IS_WSL=true
    TERM_CMD="cmd.exe /c start"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if grep -q "Kali" /etc/os-release; then
        OS_TYPE="kali"
        TERM_CMD="gnome-terminal"
    elif grep -q "Ubuntu" /etc/os-release; then
        OS_TYPE="ubuntu"
        TERM_CMD="gnome-terminal"
    elif grep -q "Arch" /etc/os-release; then
        OS_TYPE="arch"
        TERM_CMD="xfce4-terminal"
    else
        OS_TYPE="linux"
        TERM_CMD="xterm"
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
    TERM_CMD="open -a Terminal"
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS_TYPE="windows"
    TERM_CMD="cmd.exe /c start"
else
    echo "❌ Unsupported OS detected: $OSTYPE"
    exit 1
fi

echo "🖥️ Detected OS: $OS_TYPE"
echo ""

# Check essential files
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: '.env' file not found. Environment variables may be missing."
fi

if [ ! -f "frontend/package.json" ]; then
    echo "❌ Error: 'frontend/package.json' not found."
    exit 1
fi

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment (.venv) not found."
    exit 1
fi

# Check npm installation
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed."
    exit 1
fi

# Function: Launch Backend
launch_backend() {
    echo "🔵 Launching Backend (Flask API)..."
    if [[ "$OS_TYPE" == "macos" ]]; then
        osascript <<EOF
tell application "Terminal"
    do script "cd ~/nuvai && source .venv/bin/activate && flask --app server run"
end tell
EOF
    elif [[ "$OS_TYPE" == "windows" || "$OS_TYPE" == "wsl" ]]; then
        $TERM_CMD "cd %USERPROFILE%\\nuvai && .venv\\Scripts\\activate && flask --app server run"
    else
        $TERM_CMD -- bash -c "
            cd ~/nuvai || exit 1
            source .venv/bin/activate || { echo '❌ Failed to activate virtual environment'; exit 1; }
            flask --app server run || { echo '❌ Failed to start Flask server'; exit 1; }
            exec bash
        " &
    fi
}

# Function: Launch Frontend
launch_frontend() {
    echo "🟠 Launching Frontend (React App)..."
    if [[ "$OS_TYPE" == "macos" ]]; then
        osascript <<EOF
tell application "Terminal"
    do script "cd ~/nuvai/frontend && npm install && npm run dev"
end tell
EOF
    elif [[ "$OS_TYPE" == "windows" || "$OS_TYPE" == "wsl" ]]; then
        $TERM_CMD "cd %USERPROFILE%\\nuvai\\frontend && npm install && npm run dev"
    else
        $TERM_CMD -- bash -c "
            cd ~/nuvai/frontend || exit 1
            npm install || { echo '❌ npm install failed'; exit 1; }
            npm run dev || { echo '❌ Failed to start frontend server'; exit 1; }
            exec bash
        " &
    fi
}

# Function: Open Browser
open_browser() {
    echo "🌐 Opening Frontend in your browser..."
    if [[ "$OS_TYPE" == "macos" ]]; then
        open https://localhost:5173/
    elif [[ "$OS_TYPE" == "windows" || "$OS_TYPE" == "wsl" ]]; then
        cmd.exe /c start https://localhost:5173/
    else
        xdg-open https://localhost:5173/ &> /dev/null || echo "⚠️ Could not auto-open browser."
    fi
}

# Handle script arguments
if [[ "$1" == "backend" ]]; then
    # Only backend
    if lsof -i :5000 &> /dev/null; then
        echo "❌ Port 5000 already in use. Backend may already be running."
        exit 1
    fi
    launch_backend
    exit 0
elif [[ "$1" == "frontend" ]]; then
    # Only frontend
    if lsof -i :5173 &> /dev/null; then
        echo "❌ Port 5173 already in use. Frontend may already be running."
        exit 1
    fi
    launch_frontend
    exit 0
else
    # Default: launch both
    echo "🛠️ Starting FULL SYSTEM (Backend first, then Frontend)..."

    if lsof -i :5000 &> /dev/null; then
        echo "❌ Port 5000 already in use. Backend may already be running."
        exit 1
    fi

    if lsof -i :5173 &> /dev/null; then
        echo "❌ Port 5173 already in use. Frontend may already be running."
        exit 1
    fi

    launch_backend

    echo "⏳ Waiting 1 seconds to let Backend fully start..."
    sleep 1

    launch_frontend

    echo "⏳ Waiting 2 seconds before opening the browser..."
    sleep 2

    open_browser

    echo ""
    echo "✅ All systems started successfully!"
    echo ""
    echo "👉 Backend running at:  https://localhost:5000/"
    echo "👉 Frontend running at: https://localhost:5173/"
    echo ""
    echo "🎯 To stop, close the opened terminal windows or press CTRL+C inside each."
    echo ""
fi
