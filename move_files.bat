@echo off
setlocal enabledelayedexpansion

REM Ask the user for the year and the month number
set /p year="Enter the year (e.g., 2023): "
set /p number_month="Enter the month number (e.g., 1 for January): "

REM Define source and destination paths
set "source1=week_.xlsx"
set "source2=week_finished_.xlsx"
set "destination=nuvia_app_reports\data\%year%\%number_month%"

REM Check if the destination folder exists, if not, create it
if not exist "%destination%" mkdir "%destination%"

REM Move files from source to destination
move "%source1%" "%destination%"
move "%source2%" "%destination%"

echo Files moved successfully to: %destination%
pause
