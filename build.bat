@rem @license
@echo off

set msBuildDir=%WINDIR%\Microsoft.NET\Framework\v3.5

echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Cleaning build byproducts... 
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@rmdir dist\client /s /q
@rmdir dist\service /s /q
@rmdir dist\utils /s /q
@rmdir dist\doc /s /q
@rmdir build /s /q

echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Building the firewall controller... 
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
call %msBuildDir%\msbuild.exe  firewall\fwipv6\fwipv6.sln /p:Configuration=Release /l:FileLogger,Microsoft.Build.Engine;logfile=Manual_MSBuild_ReleaseVersion_LOG.log
xcopy firewall\fwipv6\bin\Release\*.* dist\utils /s /e /i

echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Building the Viper service...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python setup.py py2exe

echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Building the Viper client...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python buildexe.py

echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Copying documentation...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
xcopy doc dist\doc /s /e /i

echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Compiling windows installer...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
set mk=makensis.exe
for %%i in ("%PATH%") do if exist %%i\%mk% set found=%%i
if "%found%"=="" (
	echo "!!! NSIS doesn't seem to be installed in your system. I cannot build the Windows installer without it."
) else (
	makensis scripts\viper-installer.nsi
)