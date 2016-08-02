import sys, json, os, glob
sys.path.append(os.path.dirname(__file__) + "/defensivePairingScripts")
import simpleClosest

def getIdsFromGlob(merged_dir):
    """ Returns a list of gameids from json files in the current directory """
    # relative paths
    ids = glob.glob(merged_dir + '*.json')

    merged_dir_len = len(merged_dir)

    # get only ids from files in the current directory
    ids = list(map(lambda x: x[merged_dir_len:x.find('.')], ids))
    # return only unique ids
    ids = list(set(ids))
    return ids

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: please specify type of pairing to use, and optionally the merged files dir")
        sys.exit(1)

    if len(sys.argv) != 3:
        merged_dir = ''
    else:
        merged_dir = sys.argv[2]
        if merged_dir[:-1] != '/':
            merged_dir += '/'

    print('Using merged files found in: ' + merged_dir)

    # create export directory if needed
    os.makedirs('pairings', exist_ok=True)

    # get list of all game ids
    ids = getIdsFromGlob(merged_dir)
    print('Games to processs:')
    print(ids)

    # generate pairings
    for i in ids:
        simpleClosest.main(i, merged_dir)

if __name__ == '__main__':
    main()
