import sys
import json
import datetime
from pprint import pprint

pbp_data = []
moments_data = []

# 1. Import data specified by a the game number (CL argument)
def importData(game_id):
    with open(game_id + '-pbp.json') as pbp_json_file:
        global pbp_data
        pbp_data = json.load(pbp_json_file)

    with open(game_id + '.json') as moments_json_file:
        global moments_data
        moments_data = json.load(moments_json_file)

def createPlayersDict():
    home_players = moments_data['events'][0]['home']['players']
    visitor_players = moments_data['events'][0]['visitor']['players']
    return { 'home': home_players, 'visitor': visitor_players }

# 2. Process Play-by-play data into usable form
    # a. Need to get Player ID from moment data
    # b. Deterine player ID for each play with text analysis
    # c. Calculate UNIX time stamp if not already done
    # d. Add flag for change of possesion

def processPlayByPlayData():
    plays = []
    nba_date = moments_data['gamedate']
    game_time = pbp_data['resultSets'][0]['rowSet'][0][5]
    game_time_hour = int(game_time[:game_time.find(':')])
    if 'PM' in game_time:
        game_time_hour += 12
    game_time_minute = int(game_time[game_time.find(':') + 1:game_time.find(' ')])

    date = datetime.datetime(int(nba_date[0:4]), int(nba_date[5:7]), int(nba_date[8:10]), game_time_hour, game_time_minute)
    game_start_unix = date.timestamp()


# 2. Clean moment data
    # a. Flatten events/moments to a single array of frames
    # b. Merge in Play-by-play based on UNIX time stamp
    # c. Divide back into events based on change of possesion flag

def processMomentsData():
    events = moments_data['events']
    frames = []

    for event in events:
        for moment in event['moments']:
            # if the moment's millisecond value is not equal to the last frame's ms value
            if len(frames) == 0 or moment[1] > frames[-1][1]:
                frames.append(moment)

    # print(len(frames))

# 3. Save as new JSON file


# Other things to maybe include later:
# Player shooting stats (good defenders stay close to good shooters, and sag off bad ones)


def main():
    if len(sys.argv) != 2:
        print("usage: 123123 where 123123 is the game_id")
        sys.exit(1)

    game_id = sys.argv[1]
    importData(game_id)
    players = createPlayersDict()
    processPlayByPlayData()
    processMomentsData()

if __name__ == '__main__':
    main()
