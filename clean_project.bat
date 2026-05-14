@echo off
echo Dang xoa file rac...
del /s /q *.pyc
del /s /q *.pyo
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
if exist "duck_ops.db" del /q "duck_ops.db"
echo Da xong!
pause
