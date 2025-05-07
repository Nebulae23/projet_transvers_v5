@echo off
echo Nightfall Defenders Test Suite
echo =============================
echo.
echo Choose a test to run:
echo 1. Day/Night Cycle Basic Test
echo 2. Environment Objects Test
echo 3. Run both tests
echo 4. Exit
echo.

set /p choice=Enter your choice (1-4): 

if "%choice%"=="1" (
    echo.
    echo Running Day/Night Cycle Test...
    echo.
    call run_day_night_test.bat
) else if "%choice%"=="2" (
    echo.
    echo Running Environment Objects Test...
    echo.
    call run_environment_test.bat
) else if "%choice%"=="3" (
    echo.
    echo Running all tests sequentially...
    echo.
    echo Day/Night Cycle Test:
    echo --------------------
    call run_day_night_test.bat
    echo.
    echo Environment Objects Test:
    echo -----------------------
    call run_environment_test.bat
) else if "%choice%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run again and select 1-4.
    pause
    exit /b 1
)

echo.
echo All tests completed!
pause 