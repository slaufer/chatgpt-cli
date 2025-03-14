#!/bin/sh

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

echo "Activating virtual environment..."
. venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Install complete. Run ./run.sh to run llm-cli."
