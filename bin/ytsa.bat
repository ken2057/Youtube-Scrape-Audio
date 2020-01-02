@ECHO OFF

set CUR_DIR=%CD%
cd /d %~dp0\..

if EXIST env\Scripts\activate ( ^
    env\Scripts\activate ^
    & python main.py
    deactivate & cd /d %CUR_DIR%
) else ( ^
    python main.py & cd /d %CUR_DIR%
) 
