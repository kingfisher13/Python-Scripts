# Calculate the Plus Minus for a single game
# Exports json
# Argument 1: Game ID
# Argument 2: Pairing Algorithm that is being evaluated

import sys, json, os, glob
import requests

data = []
box_scores_json = None

def getIdsFromGlob(pairings_dir):
    """ Returns a list of gameids from json files in the given directory """
    # relative paths
    ids = glob.glob(pairings_dir + '*.json')

    pairings_dir_len = len(pairings_dir)

    # get only ids from files in the current directory
    ids = list(map(lambda x: x[pairings_dir_len:x.find('.', pairings_dir_len)], ids))
    # return only unique ids
    ids = list(set(ids))
    return ids

def importData(game_id, pairing_alg, pairings_dir):
    """ Imports Data specified by the game number and pairing algorithm """
    with open('boxScores/' + game_id + '.json') as box_scores_json_file:
        global box_scores_json
        box_scores_json = json.load(box_scores_json_file)
    with open(pairings_dir + game_id + '.json') as processed_json_file:
        global data
        data = json.load(processed_json_file)

def getBoxScoreDataFromNBASite(game_id):
    """ Download Box score data from Nba.com and export to JSON """
    if not os.path.isfile('boxScores/' + game_id + '.json'):
        url = 'http://stats.nba.com/stats/boxscoretraditionalv2?EndPeriod=10&EndRange=28800&GameID=' + game_id + '&RangeType=0&Season=2015-16&SeasonType=Regular+Season&StartPeriod=1&StartRange=0'
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
        headers = { 'user-agent' : user_agent }
        r = requests.get(url, headers=headers)
        print('Downloading box score for: ' + game_id)
        data = r.json()
        data['resultSets'][0]['rowSet'] = {x[4]: x for x in data['resultSets'][0]['rowSet']}
        with open('boxScores/' + game_id + '.json', 'w') as export:
            json.dump(data, export)

def processData():
    """
    Calculates the Plus Minus for each player for the game
    Also pulls in total minutes from the official box score.
    """
    home_players = data['players']['home']
    visitor_players = data['players']['visitor']

    for play in data['gameData']:
        if len(play[6]) != 0 and 'off' in play[6] and 'pts' in play[6]['off']:
            off = play[6]['off']
            pts = int(play[6]['off']['pts'])

            # offensive plus
            off_player = next((p for p in home_players + visitor_players if p['playerid'] == off['player_id']), None)
            if 'plusMinus' not in off_player:
                off_player['plusMinus'] = 0
            off_player['plusMinus'] += pts

            # defensive minus
            pairs = play[7]
            for pair in pairs:
                if off_player['playerid'] in pair:
                    for player in pair:
                        if player != off_player['playerid']:
                            def_player = next((p for p in home_players + visitor_players if p['playerid'] == player), None)

                            if 'plusMinus' not in def_player:
                                def_player['plusMinus'] = 0

                            def_player['plusMinus'] -= pts

    for player in home_players + visitor_players:
        if str(player['playerid']) in box_scores_json['resultSets'][0]['rowSet']:
            gametime = box_scores_json['resultSets'][0]['rowSet'][str(player['playerid'])][8]
            if gametime:
                player['minutes'] = int(gametime[0:gametime.find(':')]) + (int(gametime[gametime.find(':') + 1:]) / 60)
            else:
                player['minutes'] = 0

    return { data['teams']['home']['abbreviation']: home_players,  data['teams']['visitor']['abbreviation']: visitor_players}

def export(processed_data, game_id, pairing_alg):
    """ Exports the data into a single json file on disk """
    with open('defPlusMinus.' + pairing_alg + '/' + game_id + '.json', 'w') as export:
        json.dump(processed_data, export)

def generateAggregates(all_data):
    """ Aggregates the plus/minus into a nice json array  """
    aggregate = {}
    for game in all_data:
        for team in all_data[game]:
            for player in all_data[game][team]:
                if 'plusMinus' not in player:
                    continue

                if player['playerid'] in aggregate:
                    aggregate[player['playerid']]['aggPlusMinus'].append(player['plusMinus'])
                    aggregate[player['playerid']]['games'] += 1
                    aggregate[player['playerid']]['minutes'] += player['minutes']
                else:
                    aggregate[player['playerid']] = {
                        'playerid': player['playerid'],
                        'team': team,
                        'position': player['position'],
                        'lastname': player['lastname'],
                        'jersey': player['jersey'],
                        'firstname': player['firstname'],
                        'aggPlusMinus': [player['plusMinus']],
                        'minutes': player['minutes'],
                        'games': 1
                    }

    return {'data': list(aggregate.values())}

def calculateStats(agg, pairing_alg):
    """ Calculates averages/highs/lows from all the data """
    for player in agg['data']:
        if len(player['aggPlusMinus']) > 0:
            player[pairing_alg] = {
                'average': sum(player['aggPlusMinus']) / len(player['aggPlusMinus']),
                'max': max(player['aggPlusMinus']),
                'min': min(player['aggPlusMinus'])
            }
        else:
            player['stats'] = {
                'average': '',
                'max': '',
                'min': ''
            }

    return agg

def exportAggregate(agg, pairing_alg):
    """ Exports the data into a single json file on disk """
    with open('defPlusMinus.' + pairing_alg + '/aggregate.json', 'w') as export:
        json.dump(agg, export)

def main(pairing_alg, pairings_dir):
    # create export directory if needed
    os.makedirs('defPlusMinus.' + pairing_alg, exist_ok=True)
    os.makedirs('boxScores', exist_ok=True)

    # get list of all game ids
    ids = getIdsFromGlob(pairings_dir)
    print('Games to processs:')
    print(ids)

    # Go through game by game and generate def-plus-minus
    all_data = {}
    j = 1
    for i in ids:
        # download box scores if not already done
        getBoxScoreDataFromNBASite(i)

        # import data based on game_id
        importData(i, pairing_alg, pairings_dir)

        processed_data = processData()
        all_data[i] = processed_data
        export(processed_data, i, pairing_alg)
        print('Finished generating defensive plus/minus for: ' + i + ' (' + str(j) + ' of ' + str(len(ids)) + ')')
        j += 1

    print('Generating aggregates')
    agg = generateAggregates(all_data)
    agg = calculateStats(agg, pairing_alg)
    exportAggregate(agg, pairing_alg)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: pairing-algorithm pairings-folder(optional)")
        sys.exit(1)

    # parameters
    pairing_alg = sys.argv[1]
    if len(sys.argv) != 3:
        if os.path.isdir('pairings.' + pairing_alg):
            pairings_dir = 'pairings.' + pairing_alg + '/'
        else:
            pairings_dir = ''
    else:
        pairings_dir = sys.argv[2]
        if pairings_dir[:-1] != '/':
            pairings_dir += '/'

    main(pairing_alg, pairings_dir)
