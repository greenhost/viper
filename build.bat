@echo off
rmdir dist\client /s /q
rmdir dist\service /s /q
rmdir build /s /q
python setup py2exe
python buildexe.py

