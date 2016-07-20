import sys
import json
import datetime
from pprint import pprint

pbp_data = []
moments_data = []
players = []

def importData(game_id):
    """ Imports Data specified by the game number """
    with open(game_id + '-pbp.json') as pbp_json_file:
        global pbp_data
        pbp_data = json.load(pbp_json_file)

    with open(game_id + '.json') as moments_json_file:
        global moments_data
        moments_data = json.load(moments_json_file)

def createPlayersDict():
    """ Pulls out the player information for retrieval later """
    home_players = moments_data['events'][0]['home']['players']
    visitor_players = moments_data['events'][0]['visitor']['players']
    return { 'home': home_players, 'visitor': visitor_players }

def processPlayByPlayData():
    """ Process the Play By Play data
    Figures out the timestamp;
    Parses the playstrings """
    plays = []
    nba_date = moments_data['gamedate']
    start_time = calculateTimeFromNBATimeString(pbp_data['resultSets'][0]['rowSet'][0][5])

    date = datetime.datetime(int(nba_date[0:4]), int(nba_date[5:7]), int(nba_date[8:10]), start_time['hour'], start_time['minute'])
    game_start_timestamp = date.timestamp()

    for nba_play in pbp_data['resultSets'][0]['rowSet']:
        # generate timestamp
        play_time = calculateTimeFromNBATimeString(nba_play[5])
        play_time['seconds'] = 60 - int(nba_play[6][-2]) - 1
        timestamp = datetime.datetime(int(nba_date[0:4]), int(nba_date[5:7]), int(nba_date[8:10]), play_time['hour'], play_time['minute'], play_time['seconds']).timestamp() * 1000

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
    """ Takes an NBA time string of hour:minute and splits it """
    hour = int(timestring[:timestring.find(':')])
    if 'PM' in timestring:
        hour += 12

    minute = int(timestring[timestring.find(':') + 1:timestring.find(' ')])
    return {'hour': hour, 'minute': minute}

def whoDidWhat(details):
    """ Takes the 2 playstrings and parses them """
    home_play = parsePlay(details[0], 'home') or {}
    visitor_play = parsePlay(details[2], 'visitor') or {}

    merged = {**home_play, **visitor_play}
    return merged

def parsePlay(playstring, location):
    """ Takes a playstring
    Figures out the player mentioned.
    Figures out whether it is an offensive or defensive play. """
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

def processMomentsData():
    """ Flatten and de-duplicate moments data """
    events = moments_data['events']
    frames = []

    for event in events:
        for moment in event['moments']:
            # if the moment's millisecond value is not equal to the last frame's ms value
            if len(frames) == 0 or moment[1] > frames[-1][1]:
                frames.append(moment)

    return frames

def merge(plays, frames):
    """ Merge the play by play data with the moments data """
    return {}

def export(json_data):
    """ Exports the data into a single json file on disk """

def main():
    if len(sys.argv) != 2:
        print("usage: 123123 where 123123 is the game_id")
        sys.exit(1)

    game_id = sys.argv[1]
    importData(game_id)

    global players
    players = createPlayersDict()

    plays = processPlayByPlayData()
    frames = processMomentsData()

    merged = merge(plays, frames)
    export(merged)

if __name__ == '__main__':
    main()
