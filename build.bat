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
set FOUND=
set mk=makensis.exe
for %%i in (%mk%) do set FOUND="yes"
IF NOT DEFINED %FOUND%  (
	echo "!!! NSIS doesn't seem to be installed in your system. I cannot build the Windows installer without it."
) else (
	makensis scripts\viper-installer.nsi
)
