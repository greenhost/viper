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

:build_all
:clean
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo Cleaning build byproducts...
echo ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@rmdir dist /s /q
@rmdir build /s /q
@mkdir dist

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


:end
REM EXIT 0
