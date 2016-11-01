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

    # left or right side of the court?
    # determined by ball location of last frame
    global data
    left = data['gameData'][-1][5][0][2] < 50

    for moment in data['gameData']:
        if left:
            for player in moment[5]:
                # rotate 90 degrees
                x = player[2]
                player[2] = player[3]
                player[3] = x + 3 # +3 is to account for new court dimensions
            if len(moment) == 7:
                anno_x = moment[6][0]
                moment[6][0] = moment[6][1]
                moment[6][1] = anno_x + 3
        else:
            for player in moment[5]:
                player[2] -= 50

                # rotate 90 degrees
                x = player[2]
                player[2] = -player[3] + 50
                player[3] = x + 3 # +3 is to account for new court dimensions
            if len(moment) == 7:
                moment[6][0] -= 50

                anno_x = moment[6][0]
                moment[6][0] = -moment[6][1] + 50
                moment[6][1] = anno_x + 3


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
