"""Examples of some system, operating system and file/path chores.
   For more information, use the os and sys modules. Note that if
   you really want to use the os interactively from python you
   should use ipython.
"""
import os

# Get the name of the current file and its path
fullpath=__file__
path,filename=os.path.split(fullpath)
pathanotherway=os.path.dirname(fullpath)


# Get the name of another file in the same folder
newpath=os.path.join(path,"junk.txt")

# Test existence
os.path.exists(newpath)   # false (file does not exist)
os.path.exists(fullpath)  # true  

# Listing files
os.listdir(os.curdir)

# Change directories
os.chdir("c:/temp")      # Note the forward slash

