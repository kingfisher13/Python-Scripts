import sys, json, os, glob

def getIdsFromGlob(path):
    # absolute paths
    ids = glob.glob(path + '/*.json')

    # relative paths
    # ids = glob.glob('*.json')
    return ids

def getScriptPath():
    """ Gets the directory where the script was executed, even if __file__ doesn't exist """
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def main():
    if len(sys.argv) != 1:
        print("usage: no arguments, call in folder with moments data")
        sys.exit(1)

    directory = getScriptPath()

    # get list of all files
    ids = getIdsFromGlob(directory)

if __name__ == '__main__':
    main()
