@echo off
@REM remove the routes inserted by the OpenVPN server into our table
@REM for testing purposes
route delete 128.0.0.0
route delete 0.0.0.0 mask 128.0.0.0
