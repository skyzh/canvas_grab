#!/bin/bash

echo "Check Python installation..."
python_path=$(command -v python3 2>/dev/null)
if [ -z $python_path ]; then
    python_path=$(command -v python 2>/dev/null)
fi
eval $python_path --version

python3() {
    eval "$python_path $@"
}

set -e

echo "Check virtual environment..."

if [ ! -d "venv" ]; then
    echo "Create virtual environment..."
    python3 -m venv venv
    echo "Activate virtual environment..."
    . venv/bin/activate
    echo "Install dependencies with SJTUG mirror..."
    python -m pip install --upgrade pip -i https://mirrors.sjtug.sjtu.edu.cn/pypi/web/simple
    python -m pip install -r requirements.txt -i https://mirrors.sjtug.sjtu.edu.cn/pypi/web/simple
else
    echo "Activate virtual environment..."
    . venv/bin/activate
fi

python main.py $@
