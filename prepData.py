import sys, json, os, glob
import requests
import prepData_SingleGame

def getIdsFromGlob():
    """ Returns a list of gameids from json files in the current directory """
    # relative paths
    ids = glob.glob('*.json')

    ids = list(map(lambda x: x[:-5], ids))
    return ids

def getPbpDataFromNBASite(game_id):
    """ Download Play by play data from Nba.com and export to JSON """
    url = 'http://stats.nba.com/stats/playbyplay?GameID=' + game_id + '&RangeType=0&StartPeriod=0&EndPeriod=0&StartRange=0&EndRange=0'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    headers = { 'user-agent' : user_agent }
    r = requests.get(url, headers=headers)
    print('Downloading ' + game_id)
    with open(game_id + '-pbp.json', 'w') as export:
        json.dump(r.json(), export)

def main():
    if len(sys.argv) != 1:
        print("usage: no arguments, call in folder with moments data")
        sys.exit(1)

    # get list of all files
    ids = getIdsFromGlob()

    # get pbp data
    for i in ids:
        getPbpDataFromNBASite(i)
        prepData_SingleGame.main(i)

if __name__ == '__main__':
    main()
