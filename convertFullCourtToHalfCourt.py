# Take a set of game data, cut to only half court, and rotate 90 degrees
# Rotates so basket is on the bottom
# Exports json
# Argument 1: Game ID

import sys, json, os

data = []

def importData(game_id):
    """ Imports Data specified by the game number """
    with open(game_id + '.json') as processed_json_file:
        global data
        data = json.load(processed_json_file)

def convertData():
    """ Converts Data into half court, rotated """

def exportData(game_id):
    """ Exports Data """
    with open(game_id + '.halfcourt.json', 'w') as export:
        json.dump(data, export)

def main():
    if len(sys.argv) != 2:
        print("usage: game_id needs to be specified")
        sys.exit(1)

    importData(sys.argv[1])
    convertData()
    exportData(sys.argv[1])

if __name__ == '__main__':
    main()
