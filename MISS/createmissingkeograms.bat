@echo off
REM Running a python scripts from Task Scheduler
REM 1) activate the correct visual environment
REM 2) and, if that succeeded, run the appropriate script

call "c:\ProgramData\Anaconda3\Scripts\activate.bat" MISS-env & cd C:\Users\mikkos\MISS\Software & python createmissingRGBkeograms.py
