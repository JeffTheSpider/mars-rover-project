@echo off
echo === Backing up Mars Rover Project ===

echo.
echo --- Backup to D:\Backup ---
robocopy "D:\Mars Rover Project" "D:\Backup\Mars Rover Project" /E /XD .git .claude node_modules __pycache__ tools /XF *.png /NFL /NDL /NJH /NP /NS
echo D: backup exit code: %ERRORLEVEL%

echo.
echo --- Backup to E:\Backup ---
robocopy "D:\Mars Rover Project" "E:\Backup\Mars Rover Project" /E /XD .git .claude node_modules __pycache__ tools /XF *.png /NFL /NDL /NJH /NP /NS
echo E: backup exit code: %ERRORLEVEL%

echo.
echo === Backup complete ===
