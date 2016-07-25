import sys
import json

# globals for easy access
data = [];

def importData(game_id):
    """ Imports Data specified by the game number """
    with open('merged-data/' + game_id + '-merged.json') as processed_json_file:
        global data
        data = json.load(processed_json_file)

def main():
    if len(sys.argv) != 2:
        print("usage: 123123 where 123123 is the game_id")
        sys.exit(1)

    # import data based on game_id
    game_id = sys.argv[1]
    importData(game_id)

if __name__ == '__main__':
    main()
