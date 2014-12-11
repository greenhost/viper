@echo off
@rem Copyright (c) 2013 Greenhost VOF
@rem https://greenhost.nl -\- https://greenhost.io
@rem
@rem This program is free software: you can redistribute it and/or modify
@rem it under the terms of the GNU Affero General Public License as
@rem published by the Free Software Foundation, either version 3 of the
@rem License, or (at your option) any later version.
@rem
@rem This program is distributed in the hope that it will be useful,
@rem but WITHOUT ANY WARRANTY; without even the implied warranty of
@rem MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
@rem GNU Affero General Public License for more details.
@rem
@rem You should have received a copy of the GNU Affero General Public License
@rem along with this program. If not, see <http://www.gnu.org/licenses/>.

@echo off
set msBuildDir=%WINDIR%\Microsoft.NET\Framework\v3.5

:parsecli
IF "%~1"=="64" GOTO amd64
IF "%~1"=="32" GOTO x86

echo "Please specify '64' if you want a 64bit build or '32' if you want a 32 bit build"
goto end

@rem set variables
:x86
set BUILD="x86"
goto build_all
:amd64
set BUILD="amd64"
goto build_all

:build_all
:clean
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Cleaning build byproducts...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@rmdir dist\client /s /q
@rmdir dist\service /s /q
@rmdir dist\utils /s /q
@rmdir dist\doc /s /q
@rmdir build /s /q

:build_firewall_ctl
echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Building the firewall controller...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
call %msBuildDir%\msbuild.exe  firewall\fwipv6\fwipv6.sln /p:Configuration=Release /l:FileLogger,Microsoft.Build.Engine;logfile=Manual_MSBuild_ReleaseVersion_LOG.log
xcopy firewall\fwipv6\bin\Release\*.* dist\utils /s /e /i /y
xcopy firewall\fwipv6\bin\Release\*.exe utils /s /e /i /y

:build_service
echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Building the Viper service...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python setup.py py2exe

:build_client
echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Building the Viper client...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python buildexe.py

:doc
echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Copying documentation...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
xcopy doc dist\doc /s /e /i

:build_installer
echo.
echo.
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Compiling windows installer...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
set FOUND=
for %%i in (makensis.exe) do (set FOUND=%%~PATH:i)
IF NOT DEFINED FOUND  (
	echo "!!! NSIS doesn't seem to be installed in your system. I cannot build the Windows installer without it."
) else (
	makensis scripts\viper-installer.nsi
)

:end
EXIT 0
