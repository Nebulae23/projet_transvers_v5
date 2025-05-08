@echo off
echo Nightfall Defenders Test Suite
echo =============================
echo.
echo Choose a test to run:
echo 1. Day/Night Cycle Basic Test
echo 2. Environment Objects Test
echo 3. Enemy Psychology Test
echo 4. Night Fog Test
echo 5. Advanced Enemy Psychology Test
echo 6. Adaptive Difficulty System Test
echo 7. Run all tests
echo 8. Exit
echo.

set /p choice=Enter your choice (1-8): 

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
    echo Running Enemy Psychology Test...
    echo.
    call run_psychology_test.bat
) else if "%choice%"=="4" (
    echo.
    echo Running Night Fog Test...
    echo.
    call run_night_fog_test.bat
) else if "%choice%"=="5" (
    echo.
    echo Running Advanced Enemy Psychology Test...
    echo.
    call run_advanced_psychology_test.bat
) else if "%choice%"=="6" (
    echo.
    echo Running Adaptive Difficulty System Test...
    echo.
    call run_adaptive_difficulty_test.bat
) else if "%choice%"=="7" (
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
    echo.
    echo Enemy Psychology Test:
    echo --------------------
    call run_psychology_test.bat
    echo.
    echo Night Fog Test:
    echo -------------
    call run_night_fog_test.bat
    echo.
    echo Advanced Enemy Psychology Test:
    echo ----------------------------
    call run_advanced_psychology_test.bat
    echo.
    echo Adaptive Difficulty System Test:
    echo ----------------------------
    call run_adaptive_difficulty_test.bat
) else if "%choice%"=="8" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid choice. Please run again and select 1-8.
    pause
    exit /b 1
)

echo.
echo All tests completed!
pause 