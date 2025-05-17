# install.sh
#!/bin/bash

echo ""
echo "🚀 Starting Nuvai backend setup..."
echo ""

# Step 1: Check Python3
if [ ! -x "$(which python3)" ]; then
    echo "❌ Python3 is not installed. Please install Python 3.x before continuing."
    exit 1
fi

# Step 2: Create .venv if not exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv || {
        echo "❌ Failed to create virtual environment. Make sure 'python3-venv' is installed."
        exit 1
    }
else
    echo "🔁 Virtual environment already exists."
fi

# Step 3: Activate .venv
source .venv/bin/activate
echo "✅ Virtual environment activated."

# Step 4: Upgrade pip with fallback
echo "⬆️  Upgrading pip..."
if ! pip install --upgrade pip; then
    echo "⚠️ pip upgrade failed – trying with --break-system-packages..."
    pip install --upgrade pip --break-system-packages || echo "⚠️ Continuing anyway..."
fi

# Step 5: Install all project dependencies from requirements.txt
echo "📥 Installing all dependencies from requirements.txt..."
if ! pip install -r requirements.txt; then
    echo "⚠️ pip install failed – trying with --break-system-packages..."
    pip install -r requirements.txt --break-system-packages || {
        echo "❌ Failed to install required packages. Please check pip version and permissions."
        exit 1
    }
fi

# Step 6: Done!
echo ""
echo "🎉 Nuvai backend is ready!"
echo "👉 To run the server:"
echo "   source .venv/bin/activate && flask --app server run"
echo ""
