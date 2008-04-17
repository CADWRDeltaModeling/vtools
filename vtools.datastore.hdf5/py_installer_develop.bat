rem if exist build. rmdir /Q /S build
rem if exist dist. rmdir /Q /S dist
rem python setup.py develop egg_info  bdist_egg -p win32
python setup.py develop  