# Calculate the Plus Minus for a single game
# Exports json
# Argument 1: Game ID
# Argument 2: Pairing Algorithm that is being evaluated

import sys
import json
from pprint import pprint

data = []

def importData(game_id, pairing_alg):
    """ Imports Data specified by the game number and pairing algorithm """
    with open('merged-data/' + game_id + '-' + pairing_alg + '.json') as processed_json_file:
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

def main():
    if len(sys.argv) != 3:
        print("usage: gameid pairing-algorithm")
        sys.exit(1)

    # import data based on game_id
    game_id = sys.argv[1]
    pairing_alg = sys.argv[2]
    importData(game_id, pairing_alg)

    processed_data = processData()
    print(processed_data)

if __name__ == '__main__':
    main()
