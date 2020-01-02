@ECHO OFF

set "file="
echo - Exact file ffmpeg in bin/
wmic os get osarchitecture | findstr "64" > NUL
if errorlevel 1 ( ^
    rem 32-bit
    set file=bin/ffmpeg-32.7z
) else ( ^
    rem 64-bit  
    set file=bin/ffmpeg-64.7z
)

if exist "C:\Program Files\7-Zip\7z.exe" ( ^
    "C:\Program Files\7-Zip\7z.exe" x %file% -y -obin
) else ( ^
    if exist "C:\Program Files\WinRAR\WinRAR.exe" ( ^
        "C:\Program Files\WinRAR\WinRAR.exe" x %file% -y -o bin ^
    ) else ( ^
        echo ----------------------------------------- ^
        & echo Can't found 7zip or WinRar to extract ffmpeg in bin/ ^
        & echo Please extract it base on your OS ^
        & echo ----------------------------------------- ^
        pause
    ) ^
)

echo - Install package:
set /p answer="Do you want to use virtualenv (y/N): "

if "%answer%"=="y" ( goto :virtualenv ) ^
else ( pip install -r requirements.txt & goto :endPrint) 

:virtualenv
if not exist "env\Scripts\activate" ( echo Install virtualenv & pip install virtualenv & virtualenv env )

env\Scripts\activate ^
 & echo Install python package ^
 & pip install -r requirements.txt ^
 & deactive ^
 & echo ----------------------------------------- ^
 & echo Please add "%cd%\bin\" into Path Enviroment ^
 & echo After added, you can use "ytsa" or python %cd%\main.py to run ^
 & echo ----------------------------------------- ^
 & pause & goto :eof

:endPrint
echo ----------------------------------------- ^
 & echo Please add "%cd%\bin\" into Path Enviroment ^
 & echo After added, you can use "ytsa" or python %cd%\main.py to run ^
 & echo ----------------------------------------- ^
 & pause