# Simple closest opposing player pairings
# NOTE - will generate more than 5 pairings
# for instance, if a defender is the closest opposing player to 2 offenders
# it will pair that defender with both

import sys, json, os

# globals for easy access
data = []

def importData(game_id, merged_dir):
    """ Imports Data specified by the game number """
    with open(merged_dir + game_id + '.json') as processed_json_file:
        global data
        data = json.load(processed_json_file)

def addDefensiveAssignment():
    """ Main function for adding the defensive asssignment """
    global data
    for moment in data['gameData']:
        pairs = generatePairs(moment)
        if len(moment) != 7:
            moment.append([])
        moment.append(pairs)

def generatePairs(moment):
    """ Generate defender/offender pairs """
    pairs = []
    for player in moment[5]:
        if player[1] == -1:
            continue
        elif any(player[1] in pair for pair in pairs):
            continue
        else:
            pairs.append([player[1], findClosestOppositeTeamPlayer(player, moment[5])])

    return pairs

def findClosestOppositeTeamPlayer(player, player_locations):
    """ Finds the closest opposite team player and returns his id """
    player_team = getPlayerTeam(player[1])
    players_sorted_by_distance = orderPlayerLocations(player, player_locations)
    closest_player = [0, 0]
    for p in players_sorted_by_distance:
        if (p[1] != -1 and
            getPlayerTeam(p[1]) != player_team):
            closest_player = p
            break

    return closest_player[1]

def getPlayerTeam(id):
    """ Returns the team of the player with this id """
    team = None
    visitor = data['players']['visitor']
    for player in visitor:
        if player['playerid'] == id:
            team = 'visitor'
            break

    if team == 'visitor':
        return 'visitor'
    else:
        return 'home'

def orderPlayerLocations(player, player_locations):
    """ Returns ordered list of players by distance to given player """
    player_x = player[2]
    player_y = player[3]
    ordered = sorted(player_locations, key=lambda p: (p[2] - player_x)**2 + (p[3] - player_y)**2)

    # don't return the player (which is the closest)
    return ordered[1:]

def export(game_id):
    """ Exports the data into a single json file on disk """
    # create export directory if needed
    os.makedirs('pairings.simpleClosest', exist_ok=True)

    with open('pairings.simpleClosest/' + game_id + '.json', 'w') as export:
        json.dump(data, export)

def main(game_id, merged_dir):
    if merged_dir[:-1] != '/':
        merged_dir += '/'

    # import data based on game_id
    importData(game_id, merged_dir)

    addDefensiveAssignment()
    export(game_id)
    print('Finished generating pairings for: ' + game_id)

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("usage: 123123 where 123123 is the game_id, optional: merged directory")
        sys.exit(1)

    if len(sys.argv) == 1:
        merged_dir = ''
    else:
        merged_dir = sys.argv[2]

    main(sys.argv[1], merged_dir)
