@echo off
cd /d "%~dp0"
python -m streamlit run app.py
if errorlevel 1 (
    echo.
    echo 若提示找不到 python，请先安装 Python 并勾选 "Add to PATH"。
    echo 若提示 No module named streamlit，请先执行: python -m pip install -r requirements.txt
    pause
)
