#!/bin/bash

# Set project root
cd "$(dirname "$0")"

# 🧠 Start virtualenv
source venv/bin/activate

# 🔪 Kill any process on port 5000
echo "Killing anything on port 5000..."
lsof -ti :5000 | xargs kill -9 2>/dev/null

# 🚀 Run backend in new terminal tab
osascript <<EOF
tell application "Terminal"
    do script "cd ~/Desktop/ytd-site/backend && source ../venv/bin/activate && python app.py"
end tell
EOF

# 🌐 Run frontend in this tab
echo "Starting frontend at http://127.0.0.1:3000..."
cd frontend
python3 -m http.server 3000
