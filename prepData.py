import sys
import json

# Globals for easy access
pbp_data = []
moments_data = []
players = []
teams = []

def importData(game_id):
    """ Imports Data specified by the game number """
    with open('data/' + game_id + '-pbp.json') as pbp_json_file:
        global pbp_data
        pbp_data = json.load(pbp_json_file)

    with open('data/' + game_id + '.json') as moments_json_file:
        global moments_data
        moments_data = json.load(moments_json_file)

def createPlayersDict():
    """ Pulls out the player information for retrieval later """
    home_players = moments_data['events'][0]['home']['players']
    visitor_players = moments_data['events'][0]['visitor']['players']
    return { 'home': home_players, 'visitor': visitor_players }

def createTeamDict():
    home_team = {
        'name': moments_data['events'][0]['home']['name'],
        'teamid': moments_data['events'][0]['home']['teamid'],
        'abbreviation': moments_data['events'][0]['home']['abbreviation']
    }
    visitor_team = {
        'name': moments_data['events'][0]['visitor']['name'],
        'teamid': moments_data['events'][0]['visitor']['teamid'],
        'abbreviation': moments_data['events'][0]['visitor']['abbreviation']
    }
    return { 'home': home_team, 'visitor': visitor_team }

def processPlayByPlayData():
    """ Process the Play By Play data
    Figures out the timestamp;
    Parses the playstrings """
    plays = []
    currentMargin = 0

    for nba_play in pbp_data['resultSets'][0]['rowSet']:
        # generate timeinperiod
        timeinperiod = int(nba_play[6][:nba_play[6].find(':')]) * 60 + int(nba_play[6][nba_play[6].find(':') + 1:]) + 2

        # parse the various playstrings
        wdw = whoDidWhat(nba_play[7:10], nba_play[13:16], nba_play[20:23], nba_play[27:30]) or {}

        play = {
            'eventid': nba_play[1],
            'eventmsgtype': nba_play[2],
            'eventmsgactiontype': nba_play[3],
            'period': nba_play[4],
            'timeinperiod': timeinperiod,
            **wdw
        }

        if 'off' in play and nba_play[11]:
            if nba_play[11] == 'TIE':
                margin = 0
            else:
                margin = int(nba_play[11])
            point_value = abs(currentMargin - margin)
            currentMargin = margin
            play['off']['pts'] = point_value

        plays.append(play)

    return plays

def whoDidWhat(details, player_1, player_2, player_3):
    """ Takes the 2 playstrings and parses them to find out offense or defense"""
    home_play = parsePlay(details[0], 'home', player_1, player_2, player_3) or {}
    visitor_play = parsePlay(details[2], 'visitor', player_1, player_2, player_3) or {}

    if home_play:
        playstring = details[0]
    elif visitor_play:
        playstring = details[2]
    else:
        playstring = details[1]

    merged = {**home_play, **visitor_play, 'playstring': playstring}
    return merged

def parsePlay(playstring, location, player_1, player_2, player_3):
    """ Takes a playstring, home/away value, and the 3 players potentially involved
    Figures out whether it is an offensive or defensive play. """
    if not playstring:
        return;

    offensivePlays = ['Dunk', 'Jump Shot', 'Bank Shot', 'Dunk Shot', 'Layup', 'Jumper', 'Hook', '3PT', 'MISS', 'Turnover', 'Free Throw', 'Offensive Charge Foul']
    defensivePlays = ['STEAL', 'BLOCK', 'L.B.FOUL', 'P.FOUL', 'S.FOUL', 'Shooting Block Foul', 'Personal Block Foul', 'T.Foul', 'Personal Take Foul']

    if any(oplay in playstring for oplay in offensivePlays):
        side = 'off'
        player_id = player_1[0]
        player_team_id = player_1[2]
    elif any(dplay in playstring for dplay in defensivePlays):
        side = 'def'
        if player_2:
            player_id = player_2[0]
            player_team_id = player_2[2]
        else:
            player_id = player_3[0]
            player_team_id = player_3[2]
    else:
        side = 'nue-' + location
        player_id = player_1[0]
        player_team_id = player_1[2]

    return {
        side: {
            'player_id': player_id,
            'playstring': playstring,
            'player_team_id': player_team_id
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
    play_index = 0

    frames_index = 0
    for i, p in enumerate(plays):
        period = p['period']

        # periods don't match
        if period != frames[frames_index][0]:
            if period > frames[frames_index][0]:
                while period != frames[frames_index][0]:
                    frames_index += 1
            elif period < frames[frames_index][0]:
                continue

        # periods match
        # play matches a frame (or close to it)
        if abs(p['timeinperiod'] - frames[frames_index][2]) <= 0.03:
            frames[frames_index].append(p)
            frames_index += 1
            continue
        # play is before any frames in the period
        elif p['timeinperiod'] > frames[frames_index][2]:
            continue
        # play is ahead of the current frame
        elif p['timeinperiod'] < frames[frames_index][2]:
            while p['timeinperiod'] < frames[frames_index][2] and p['timeinperiod'] != 0:
                frames_index += 1
            if abs(p['timeinperiod'] - frames[frames_index][2]) <= 0.03:
                frames[frames_index].append(p)
                frames_index += 1
                continue

    return frames

def export(json_data, game_id):
    """ Exports the data into a single json file on disk """
    final = {
        'players': players,
        'teams': teams,
        'gameData': json_data,
        'gameDate': moments_data['gamedate'],
        'gameId': game_id
    }
    with open('merged-data/' + game_id + '-merged.json', 'w') as export:
        json.dump(final, export)

def main():
    if len(sys.argv) != 2:
        print("usage: 123123 where 123123 is the game_id")
        sys.exit(1)

    # import data based on game_id
    game_id = sys.argv[1]
    importData(game_id)

    # get the players and teams
    global players
    players = createPlayersDict()
    global teams
    teams = createTeamDict()

    # process and merge the data
    plays = processPlayByPlayData()
    frames = processMomentsData()
    merged = merge(plays, frames)

    # export
    export(merged, game_id)

if __name__ == '__main__':
    main()
