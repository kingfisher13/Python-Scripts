# Calculate the Plus Minus for a single game
# Exports json
# Argument 1: Game ID
# Argument 2: Pairing Algorithm that is being evaluated

import sys, json, os, glob

data = []

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
    with open(pairings_dir + game_id + '.json') as processed_json_file:
        global data
        data = json.load(processed_json_file)

def processData():
    """ Calculates the Plus Minus for each player for the game """
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
                else:
                    aggregate[player['playerid']] = {
                        'playerid': player['playerid'],
                        'team': team,
                        'position': player['position'],
                        'lastname': player['lastname'],
                        'jersey': player['jersey'],
                        'firstname': player['firstname'],
                        'aggPlusMinus': [player['plusMinus']]
                    }

    return {'data': list(aggregate.values())}

def calculateStats(agg):
    """ Calculates averages/highs/lows from all the data """
    for player in agg['data']:
        if len(player['aggPlusMinus']) > 0:
            player['stats'] = {
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

    # get list of all game ids
    ids = getIdsFromGlob(pairings_dir)
    print('Games to processs:')
    print(ids)

    # Go through game by game and generate def-plus-minus
    all_data = {}
    j = 1
    for i in ids:
        # import data based on game_id
        importData(i, pairing_alg, pairings_dir)

        processed_data = processData()
        all_data[i] = processed_data
        export(processed_data, i, pairing_alg)
        print('Finished generating defensive plus/minus for: ' + i + ' (' + str(j) + ' of ' + str(len(ids)) + ')'')
        j += 1

    print('Generating aggregates')
    agg = generateAggregates(all_data)
    agg = calculateStats(agg)
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
