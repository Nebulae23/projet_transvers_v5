@echo off
echo Starting Environment Objects Test
echo.
echo This test demonstrates environmental objects that change with the day/night cycle:
echo - Lanterns that turn on at dusk and night
echo - Fireflies that appear during dusk and night
echo.
echo Controls:
echo 1-5: Set time of day (Dawn, Day, Dusk, Night, Midnight)
echo +/-: Adjust time scale
echo Arrow keys: Rotate camera
echo R: Reset camera view
echo.
python src/tests/test_environment_objects.py
pause 