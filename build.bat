@echo off
echo [STEP 1/3] Deleting old build directories...
rd /s /q dist build
if exist FirewallChecker.spec del FirewallChecker.spec

echo.
echo [STEP 2/3] Building executable with PyInstaller...
call venv\Scripts\pyinstaller.exe --windowed --name FirewallChecker --hidden-import="playwright" --hidden-import="scraper" --hidden-import="scheduler" --hidden-import="nslookup_ipv4" --add-data "tuples_list.json;." --add-data "domain_list.json;." gui.py

rem Check if the build was successful before copying
if not exist "dist\FirewallChecker" (
    echo.
    echo ERROR: PyInstaller build failed. Exiting.
    pause
    exit /b
)

echo.
echo [STEP 3/3] Copying Playwright browser files...
xcopy C:\Users\kwic\AppData\Local\ms-playwright dist\FirewallChecker\_internal\playwright\driver\package\.local-browsers /E /I /Y

echo.
echo ==================================
echo  Build process complete!
echo  You can find the executable in the 'dist\FirewallChecker' folder.
echo ==================================
echo.
pause
