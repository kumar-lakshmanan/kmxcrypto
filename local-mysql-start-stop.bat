@echo off
:: === Auto-Elevate to Administrator ===
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

:: === Define service name ===
set SERVICE=MySQL80

:: === Check service state ===
for /f "tokens=3 delims= " %%A in ('sc query "%SERVICE%" ^| findstr "STATE"') do set STATUS=%%A

echo Current status of %SERVICE%: %STATUS%

if /i "%STATUS%"=="4" (
    echo Stopping %SERVICE%...
    sc stop "%SERVICE%"
) else if /i "%STATUS%"=="1" (
    echo Starting %SERVICE%...
    sc start "%SERVICE%"
) else (
    echo Service %SERVICE% is in a transitional state: %STATUS%
)

pause
