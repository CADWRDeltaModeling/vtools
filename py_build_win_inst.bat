if exist build. rmdir /Q /S build
if exist dist. rmdir /Q /S dist
python setup.py bdist --format=wininst 
