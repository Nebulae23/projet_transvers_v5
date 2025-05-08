@echo off
echo Starting Nightfall Defenders
echo.
echo Controls:
echo WASD - Move player
echo Mouse1 - Attack
echo Mouse3 - Secondary attack
echo Space - Dodge
echo E - Interact
echo C - Crafting menu
echo R - Relics menu
echo B - Building menu
echo T - Toggle between day and night
echo F1 - Toggle debug info
echo.
echo New Features:
echo - Day/Night Cycle affects gameplay:
echo   - More enemies spawn at night
echo   - Night enemies are stronger
echo   - Visibility is reduced at night
echo.

rem Set Python path to current directory for imports
set PYTHONPATH=%CD%

rem Run the game
python src/game/main.py

echo Game closed. 