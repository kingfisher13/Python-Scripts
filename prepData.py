import sys, json, os, glob

def getIdsFromGlob():
    """ Returns a list of json files in the current directory """
    # relative paths
    ids = glob.glob('*.json')
    return ids

def main():
    if len(sys.argv) != 1:
        print("usage: no arguments, call in folder with moments data")
        sys.exit(1)

    # get list of all files
    ids = getIdsFromGlob()
    print(ids)

if __name__ == '__main__':
    main()
