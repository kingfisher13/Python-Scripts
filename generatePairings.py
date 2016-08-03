import sys, json, os, glob
sys.path.append(os.path.dirname(__file__) + "/defensivePairingScripts")
import simpleClosest

def getIdsFromGlob(merged_dir):
    """ Returns a list of gameids from json files in the given directory """
    # relative paths
    ids = glob.glob(merged_dir + '*.json')

    merged_dir_len = len(merged_dir)

    # get only ids from files in the current directory
    ids = list(map(lambda x: x[merged_dir_len:x.find('.')], ids))
    # return only unique ids
    ids = list(set(ids))
    return ids

def getAlgFunction(pairing_alg):
    if pairing_alg == 'simpleClosest':
        return simpleClosest

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: pairing-algorithm merged-files-directory(optional)")
        sys.exit(1)

    # parameters
    pairing_alg = sys.argv[1]
    if len(sys.argv) != 3:
        if os.path.isdir('merged'):
            merged_dir = 'merged/'
        else:
            merged_dir = ''
    else:
        merged_dir = sys.argv[2]
        if merged_dir[:-1] != '/':
            merged_dir += '/'

    print('Using merged files found in: ' + merged_dir)

    # get list of all game ids
    ids = getIdsFromGlob(merged_dir)
    print('Games to processs:')
    print(ids)

    # generate pairings
    j = 1
    for i in ids:
        getAlgFunction(pairing_alg).main(i, merged_dir)
        print('(' + str(j) + ' of ' + str(len(ids)) + ')')
        j += 1

if __name__ == '__main__':
    main()
