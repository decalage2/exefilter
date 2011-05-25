@echo off

if exist thirdparty\movpy-2.0.0-py2.5.1\movpy\movpy.exe goto RUN

echo Portable ExeFilter requires Movable Python to be copied in the directory
echo thirdparty\movpy-2.0.0-py2.5.1
echo.
echo Please see README_portable.txt and http://www.decalage.info/exefilter/portable
echo.
pause
goto END

:RUN
thirdparty\movpy-2.0.0-py2.5.1\movpy\movpy.exe -f ExeFilter_GUI.py
goto END

:END