if exist build. rmdir /Q /S build
if exist dist. rmdir /Q /S dist
python setup.py egg_info  bdist_egg -p win32
