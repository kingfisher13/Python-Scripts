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

def main():
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

    # create export directory if needed
    os.makedirs('defPlusMinus.' + pairing_alg, exist_ok=True)

    # get list of all game ids
    ids = getIdsFromGlob(pairings_dir)
    print('Games to processs:')
    print(ids)

    # Go through game by game and generate def-plus-minus
    for i in ids:
        # import data based on game_id
        importData(i, pairing_alg, pairings_dir)

        processed_data = processData()
        export(processed_data, i, pairing_alg)
        print('Finished generating defensive plus/minus for: ' + i)

if __name__ == '__main__':
    main()
