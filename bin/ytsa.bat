@ECHO OFF

cd /d %~dp0\..

if EXIST env\Scripts\activate ( ^
    env\Scripts\activate ^
    & cls ^
    & python main.py
) else ( ^
    python main.py
)
