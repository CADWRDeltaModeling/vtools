"""Example script with arguments.
   This style will make it easier to use your script in several settings:
   1. Called from another script with new data
   2. Used as a standalone script or with the config.py system
   3. Called from a batch file

   Ideally, the module should have an docstring describing its use.
   The module name should match the most important public function in the module. 
"""

from optparse import OptionParser

def script_style(first, second, myinteger,ending = "!!!"):
     """The most important public function returns a string.
        Note this function will ordinarily have data arguments, not files or file names.
        Arguments:
        first string, not None
        second string, may be omitted
        myint an integer less than 5
     """
     # Argument checking
     if (first is None):
         raise TypeError("Raise this error for None")
     if type(myinteger) != int:
         print myinteger
         raise TypeError("myint should be an integer.")
     if myinteger >=5:
         raise ValueError("ValueError for right type, inappropriate value")
     
     message="Hello world %s %s %s %s" % (first, second, myinteger,ending)
     print message
     return message

def main():
    """Standalone runnable main function
    This function will ordinarily know how to get the arguments it needs, either from
    defaults, a config system or options parsing (which makes batch files easier).

    This example uses options parsing with optparse.

    OK, a fair question is 'what is options parsing'. Lets say you want to run a script
    from the command line. Assuming Python is the default for *.py files, you type:
      >script_style.py --first=hello --second=goodbye -i 4 ????
    We are using optparse, and the code below registers --first, --second and -i
    as option flags. The command above assigns them values hello, goodbye and 4
    respectively. There is also a hidden --help option, and if you type
      >scriptstyle.py --help
    you will see what it does.

    Anything after all the options (???? in this case) is an argument to python. It
    gets stored in a list called sys.argv. You would can get at them if you
    type
    import sys
    print sys.argv

    However, since we are using optparse, it does this for us behind the scenes.
    
    """
    # parse command line options
    usage = "script_style.py [options] punctuation"
    parser=OptionParser(usage)
    try:
        parser.add_option("-f","--first",dest="first",help="a string, follows 'world'")
        parser.add_option("-s","--second",dest="second",help="another string, follows FIRST")
        parser.add_option("-i","--integer",action="store",dest="myint",type="int",help="integer arg")

        (opts, args) = parser.parse_args()
        if len(args) != 1:
            parser.error("incorrect number of arguments")        
        ending=args[0]
        script_style(opts.first,opts.second,opts.myint,ending)
                
    except StandardError, e:
        print e

    

def test():
    """Simple test
    This is a good place to put a simple test if this is possible.
    """
    script_style("a","b",3)
    try:
        script_style("a","b",6)
        raise "Bad argument not identified"
    except ValueError:
        print "Exception caught as expected"
    return






if __name__ == "__main__":
    main()                   # Always call main() here and let it do the work

     


 
