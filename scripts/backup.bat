@echo off
echo ============================================
echo   Mars Rover Project Backup
echo ============================================
echo.

echo Backing up to C:\Backups...
robocopy "D:\Mars Rover Project" "C:\Backups\Mars Rover Project" /MIR /XD .git __pycache__ node_modules build /NFL /NDL /NJH /NJS /NC /NS
echo.

echo Backing up to E:\Backup...
robocopy "D:\Mars Rover Project" "E:\Backup\Mars Rover Project" /MIR /XD .git __pycache__ node_modules build /NFL /NDL /NJH /NJS /NC /NS
echo.

echo ============================================
echo   Backup complete!
echo ============================================
