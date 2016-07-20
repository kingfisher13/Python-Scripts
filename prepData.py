import sys
import json
import datetime
from pprint import pprint

pbp_data = []
moments_data = []
players = []

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
    start_time = calculateTimeFromNBATimeString(pbp_data['resultSets'][0]['rowSet'][0][5])

    date = datetime.datetime(int(nba_date[0:4]), int(nba_date[5:7]), int(nba_date[8:10]), start_time['hour'], start_time['minute'])
    game_start_timestamp = date.timestamp()

    for nba_play in pbp_data['resultSets'][0]['rowSet']:
        # generate timestamp
        play_time = calculateTimeFromNBATimeString(nba_play[5])
        play_time['seconds'] = 60 - int(nba_play[6][-2]) - 1
        timestamp = datetime.datetime(int(nba_date[0:4]), int(nba_date[5:7]), int(nba_date[8:10]), play_time['hour'], play_time['minute'], play_time['seconds']).timestamp()

        # parse the various playstrings
        wdw = whoDidWhat(nba_play[7:10]) or {}

        play = {
            'eventnum': nba_play[1],
            'eventmsgtype': nba_play[2],
            'eventmsgactiontype': nba_play[3],
            'period': nba_play[4],
            'timestamp': int(timestamp),
            **wdw
        }

        plays.append(play)

    return plays

def calculateTimeFromNBATimeString(timestring):
    hour = int(timestring[:timestring.find(':')])
    if 'PM' in timestring:
        hour += 12

    minute = int(timestring[timestring.find(':') + 1:timestring.find(' ')])
    return {'hour': hour, 'minute': minute}

def whoDidWhat(details):
    home_play = parsePlay(details[0], 'home') or {}
    visitor_play = parsePlay(details[2], 'visitor') or {}

    merged = {**home_play, **visitor_play}
    return merged

def parsePlay(playstring, location):
    if not playstring:
        return;

    player_id = None
    playstring_players = []

    for player in players[location]:
        if player['lastname'] in playstring:
            playstring_players.append(player)

    highest_count_of_duplicate_lastnames = 0
    for player in playstring_players:
        count_of_lastnames = len([p for p in players[location] if p['lastname'] == player['lastname']])
        if count_of_lastnames > highest_count_of_duplicate_lastnames:
            highest_count_of_duplicate_lastnames = count_of_lastnames

    if len(playstring_players) == 1:
        player_id = playstring_players[0]['playerid']
    elif len(playstring_players) > 1:
        playstring_arr = playstring.split()
        for i, val in enumerate(playstring_arr):
            for p in playstring_players:
                if val == p['lastname']:
                    if highest_count_of_duplicate_lastnames == 1:
                        player_id = p['playerid']
                        break;
                    elif playstring_arr[i-1:i+1] == [p['firstname'][:1] + '.', p['lastname']]:
                        player_id = p['playerid']
                        break;

    offensivePlays = ['Dunk', 'Jump Shot', 'Bank Shot', 'Dunk Shot', 'Layup', 'Jumper', 'Hook', '3PT', 'MISS', 'Turnover', 'Free Throw', 'Offensive Charge Foul']
    defensivePlays = ['STEAL', 'BLOCK', 'L.B.FOUL', 'P.FOUL', 'S.FOUL', 'Shooting Block Foul', 'Personal Block Foul', 'T.Foul', 'Personal Take Foul']

    if any(oplay in playstring for oplay in offensivePlays):
        side = 'off'
    elif any(dplay in playstring for dplay in defensivePlays):
        side = 'def'
    else:
        side = 'nue-' + location

    return {
        side: {
            'player_id': player_id,
            'playstring': playstring
        }
    }

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


# 3. Save as new JSON file


# Other things to maybe include later:
# Player shooting stats (good defenders stay close to good shooters, and sag off bad ones)


def main():
    if len(sys.argv) != 2:
        print("usage: 123123 where 123123 is the game_id")
        sys.exit(1)

    game_id = sys.argv[1]
    importData(game_id)
    global players
    players = createPlayersDict()
    processPlayByPlayData()
    # processMomentsData()

if __name__ == '__main__':
    main()
