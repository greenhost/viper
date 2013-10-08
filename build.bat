@rem Copyright (c) 2013 Greenhost VOF and contributors
@rem 
@rem Redistribution and use in source and binary forms, with or without
@rem modification, are permitted provided that the following conditions are met: 
@rem 
@rem 1. Redistributions of source code must retain the above copyright notice, this
@rem    list of conditions and the following disclaimer. 
@rem 2. Redistributions in binary form must reproduce the above copyright notice,
@rem    this list of conditions and the following disclaimer in the documentation
@rem    and/or other materials provided with the distribution. 
@rem 
@rem THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
@rem ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
@rem WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
@rem DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
@rem ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
@rem (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
@rem LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
@rem ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
@rem (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
@rem SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
@rem 
@rem The views and conclusions contained in the software and documentation are those
@rem of the authors and should not be interpreted as representing official policies, 
@rem either expressed or implied, of the FreeBSD Project.
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