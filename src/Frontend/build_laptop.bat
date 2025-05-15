@echo off
rem  --------  package_root.bat  --------
rem  Creates  package\MyApp.exe  +  package\plugins\...
rem  EDIT the three paths below, then run the script.

setlocal

set "APP=C:\Users\matia\My Drive\BABA\NAPPA-ISA\src\Frontend\x64\Release\NAPPA-ISA Client.exe"
set "STAGE=C:\Users\matia\My Drive\BABA\NAPPA-ISA\bin"
set "QT_BIN=C:\Qt\6.7.3\msvc2022_64\bin"

echo(
echo  Packaging "%APP%"
echo  into       "%STAGE%"
echo(

rem 1. make root + plugin dir
if not exist "%STAGE%"            mkdir "%STAGE%"
if not exist "%STAGE%\plugins"    mkdir "%STAGE%\plugins"

rem 2. copy the EXE
copy /y "%APP%" "%STAGE%\" >nul

rem 3. grab the file name only
for %%F in ("%APP%") do set "APP_BASENAME=%%~nxF"

rem 4. minimal qt.conf pointing at plugins sub-dir
(
  echo [Paths]
  echo Plugins=plugins
) > "%STAGE%\qt.conf"

rem 5. run windeployqt (no --libdir, dlls land in root)
"%QT_BIN%\windeployqt.exe" ^
        --release ^
        --dir        "%STAGE%" ^
        --plugindir  "%STAGE%\plugins" ^
        --compiler-runtime ^
        --no-translations ^
		--no-opengl-sw ^
		--no-system-d3d-compiler ^
        "%STAGE%\%APP_BASENAME%"

if errorlevel 1 (
    echo(
    echo *** windeployqt reported an error – check paths above. ***
) else (
    echo(
    echo Portable package created successfully in:
    echo   "%STAGE%"
)

echo(
echo =====  Finished – press any key to close  =====
pause >nul
endlocal
