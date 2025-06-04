:: Check for admin rights
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

D:\cloud-sql-proxy --credentials-file G:\pyworkspace\resources\kmx-serviceaccount.json kaymatrix:us-central1:mycryptodb
