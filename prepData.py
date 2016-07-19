import sys
import json
from pprint import pprint


# 1. Import data specified by a the game number (CL argument)
def importData(game_id):
    f = open(game_id + '-pbp.json', 'rU')

    with open(game_id + '-pbp.json') as pbp_json_file:
        pbp_data = json.load(pbp_json_file)

    pprint(pbp_data['parameters']['GameID'])

# 2. Process Play-by-play data into usable form
    # a. Need to get Player ID from moment data
    # b. Deterine player ID for each play with text analysis
    # c. Calculate UNIX time stamp if not already done
    # d. Add flag for change of possesion
# 2. Clean moment data
    # a. Flatten events/moments to a single array of frames
    # b. Merge in Play-by-play based on UNIX time stamp
    # c. Divide back into events based on change of possesion flag
# 3. Save as new JSON file


# Other things to maybe include later:
# Player shooting stats (good defenders stay close to good shooters, and sag off bad ones)


def main():
    if len(sys.argv) != 2:
        print("usage: 123123 where 123123 is the game_id")
        sys.exit(1)

    game_id = sys.argv[1]
    importData(game_id)

if __name__ == '__main__':
    main()
