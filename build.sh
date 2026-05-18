#!/bin/bash
set -e

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Checking Node.js availability..."
which node || (echo "Node.js not found, installing..." && apt-get update && apt-get install -y nodejs npm)

echo "Building frontend..."
cd frontend
echo "Installing frontend dependencies..."
npm install --legacy-peer-deps || npm install
echo "Building frontend assets..."
npm run build
echo "Frontend built to: $(pwd)/dist"
cd ..

echo "Verifying frontend build..."
if [ -f "frontend/dist/index.html" ]; then
    echo "✓ Frontend build successful"
else
    echo "✗ Frontend build failed - index.html not found"
    exit 1
fi

echo "Build complete!"
