# Calculate the Plus Minus for a single game
# Exports json
# Argument 1: Game ID
# Argument 2: Pairing Algorithm that is being evaluated

import sys
import json

data = []

def importData(game_id, pairing_alg):
    """ Imports Data specified by the game number and pairing algorithm """
    with open('merged-data/' + game_id + '-' + pairing_alg + '.json') as processed_json_file:
        global data
        data = json.load(processed_json_file)



def main():
    if len(sys.argv) != 3:
        print("usage: gameid pairing-algorithm")
        sys.exit(1)

    # import data based on game_id
    game_id = sys.argv[1]
    pairing_alg = sys.argv[2]
    importData(game_id, pairing_alg)

if __name__ == '__main__':
    main()
