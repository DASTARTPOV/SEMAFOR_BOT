import os
import sys
from api import *
from random import choice

# Be the first to get a line of three pieces of the same color horizontally, vertically or diagonally.

# Each player shares:
# 8 green, 8 yellow and 8 red pieces.

# On each turn, each player performs one of the following actions:
# - ' ' -> 'G': Place a green piece on an empty square;
# - 'G' on 'Y': Replace a green piece with a yellow piece;
# - 'Y' on 'R': Replace a yellow piece with a red piece.

# Please note that the red pieces cannot be replaced. This means that the game must always end: 
# as the board fills with red pieces, it is inevitable that a line of three pieces will appear.

def calc_stats(field):
    symbol_stats = {' ': 0, 'R' : 0, 'G' : 0, 'Y' : 0}
    for row in field:
        for cell in row:
            symbol_stats[cell] += 1
    return symbol_stats

def calc_colors_left(field):
    s = calc_stats(field)
    mx = 8
    colors_left = {'R' : mx - s['R'], 'G' : mx - s['G'], 'Y' : mx - s['Y']}
    return colors_left

def get_available_steps(field):
    left = calc_colors_left(field)

    actions = []
    for y, row in enumerate(field):
        for x, cur in enumerate(row):
            nxt = g_next_letter[cur]
            if(nxt and left[nxt]):
                actions.append((y, x))

    return actions

def apply_action(field, pos):
    y, x = pos
    nfield = field[:]
    nfield[y] = nfield[y][:]
    nfield[y][x] = g_next_letter[nfield[y][x]]
    return nfield

def win(field):
    standart = 0
    n = 0
    for y in range(field_size_y): # horizontal win checker
        for x in range(field_size_x):
            if (standart == 0 and field[y][x] != ' '):
                standart = field[y][x]
            if(field[y][x] == standart):
                n += 1
            elif(n < 3):
                n = 0
                if(field[y][x] != ' '):
                    standart = field[y][x]
                else:
                    standart = 0
        if (n >= 3):
            return True
        else:
            n = 0
    
    standart = 0
    n = 0
    for x in range(field_size_x): # vertical win checker
        for y in range(field_size_y):
            if (standart == 0 and field[y][x] != ' '):
                standart = field[y][x]
            if(field[y][x] == standart):
                n += 1
            elif(n < 3):
                n = 0
                if(field[y][x] != ' '):
                    standart = field[y][x]
                else:
                    standart = 0
        if (n >= 3):
            return True    
        else:
            n = 0
    
    standart = 0
    n = 0    
    for c in range(2): # left-down diagonal win checker
        for i in range(3):
            if (standart == 0 and field[i][c+i] != ' '):
                standart = field[i][c+i]
            if(field[i][c+i] == standart):
                n = n + 1
        if(n == 3):
            return True
        else:
            standart = 0
            n = 0             

    standart = 0
    n = 0    
    for c in range(3, 1, -1): # right-down diagonal win checker
        for i in range(3):
            if (standart == 0 and field[i][c-i] != ' '):
                standart = field[i][c-i]
            if(field[i][c-i] == standart):
                n = n + 1
        if(n == 3):
            return True
        else:
            standart = 0
            n = 0           
    
    return False

def find_good_place_to_action(field):
    to_do_not_lost = []
    possibles = get_available_steps(field)
    if(not possibles):
        return None
    for pos in possibles:
        check = apply_action(field, pos)
        if(win(check) == True):
            print(str(pos) + "  --- WIN")
            return pos
        else:
            enemy_possibles = get_available_steps(check)
            if (enemy_possibles != None):
                for var in enemy_possibles:
                    enemy_check = apply_action(check, var)
                    if(win(enemy_check) == True):
                        var = '0' #(10, 10)
                        break
                if(var != '0'):
                    to_do_not_lost.append(pos)



    # Choice random of them
    print("Choose random of %u" % len(to_do_not_lost))
    pos = choice(to_do_not_lost)
    print(pos)
    #print("RES\n%s" % dump_field(field, highlight=pos))
    return pos

def selftest():
    field = create_empty_field()
    field[0][0] = 'R'
    steps = get_available_steps(field)
    assert len(steps) == (4 * 3 - 1)

    field = create_empty_field()
    nfield = apply_action(field, (2,2))
    assert calc_stats(field)[' '] == 12
    assert calc_stats(nfield)[' '] == 11

    assert not win(create_empty_field("    \nG GG\n    "))
    assert not win(create_empty_field("    \n  GG\nG   "))
    assert not win(create_empty_field("GG  \n    \n    "))
    assert win(create_empty_field("    \n GGG\n    "))
    assert win(create_empty_field("    \nGGGG\n    "))
    assert win(create_empty_field("    \n RRR\n    "))
    assert win(create_empty_field("    \nGGG \n    "))
    assert win(create_empty_field("RR  \nGGG \n    "))

    assert not win(create_empty_field("G   \n    \nG   "))
    assert not win(create_empty_field("G   \nG   \n    "))
    assert not win(create_empty_field("  G \n   G\n   G"))
    assert win(create_empty_field(" G  \n G  \n G  "))
    assert win(create_empty_field("GGRR\n GRR\n G  "))
    
    assert win(create_empty_field("GRYR\nYGGR\n  G "))
    assert win(create_empty_field(" GGY\nYRGG\nY  G"))

    assert win(create_empty_field(" G  \n  G \n   G"))
    assert win(create_empty_field("G   \n G  \n  G "))
    
    assert find_good_place_to_action(create_empty_field("GGRR\nRRGG\nG  Y")) != (10, 10)
    assert find_good_place_to_action(create_empty_field("G  G\n R  \nR  Y")) not in [(0, 1), (0, 2)]
    for i in range(30):
        assert find_good_place_to_action(create_empty_field("    \n    \nY  G")) != (2, 2)        

    print("Selftest OK")
    

def play_game(api, debug = False):
    # Join game
    a = api.join(debug=debug)
    if a[0] == False:
        if(a[1] == 'AlreadyInGame'):
          pass
        else:
          raise Exception(f'{a[1]}: {a[2]}')
    print(f"{a[1]}: {a[2]}")

    # Main loop
    a = api.wait_turn()
    while a[0]:
        pos = None
        if 'action' in api.actions:  # If can fire (may be setup)
            field = api.game.field
            pos = find_good_place_to_action(field)
            if pos is not None:
                print(dump_field(field, highlight = pos))
        if not pos:
            print(f"Invalid state: no actions found")
            pos = (0,0)
        print(f"My step: {a}\n%s" % dump_field(field, highlight=pos))
        a = api.action(pos)
        a = api.wait_turn()
        print(f"Wait response: {a}")
    print(f"Final: {a[1]}: {a[2]}")

def main(debug = False):
    #  Creates api object
    token = open("token.txt","rt").read().strip() # os.environ['TOKEN']
    debug = ('DEBUG' in os.environ) or ('--debug' in sys.argv) or debug
    while(True):
        print("-" * 50)
        print("NEW GAME")
        print("-" * 50)
        api = Api(token=token)
        play_game(api, debug = debug)
        break

if __name__ == "__main__":
    selftest()
    if ('--selftest' in sys.argv): sys.exit(0)
#    main(debug = True)