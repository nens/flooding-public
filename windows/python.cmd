@echo off
set mypath=%~dp0
set PYTHONPATH=%mypath%lib;%PYTHONPATH%
set BUILDOUT_DIR=%mypath%
set DJANGO_SETTINGS_MODULE=flooding.windows
"D:\Python27\python.exe" %*
