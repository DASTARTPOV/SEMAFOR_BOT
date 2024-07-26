from typing import *
import requests as req
import json

field_size_x = 4
field_size_y = 3

g_color_to_letter = {'Empty': ' ', 'Red': 'R', 'Green': 'G', 'Yellow': 'Y'}
g_letter_to_color = {' ': 'Empty', 'R': 'Red', 'G': 'Green', 'Y': 'Yellow'}
g_next_letter = {' ': 'G', 'G': 'Y', 'Y': 'R', 'R': None}

def color_to_letter(color):
    return g_color_to_letter[color]

def letter_to_color(letter):
    return g_letter_to_color[letter]

def is_valid_pos(pos):
    y, x = pos
    return x >= 0 and x < field_size_x and y >= 0 and y < field_size_y

def is_valid_letter(c):
    return c in g_letter_to_color

def dump_field(field, highlight = None):
    if(highlight is not None): 
      old = field[highlight[0]][highlight[1]]
      field[highlight[0]][highlight[1]] += "!" #g_next_letter[old]
    #print(field)
    res = "|" + ("|\n|".join(["|".join([" %-02s" % x for x in row]) for row in field])) + "|"
    if(highlight is not None): 
      field[highlight[0]][highlight[1]] = old
    return res


def create_empty_field(init_str = None):
    if not(init_str is None):
       rows = init_str.split("\n")
       assert len(rows) == field_size_y
       field = [[c for c in row] for row in rows]
       assert all([len(row) == field_size_x for row in rows])
       return field
    return [[' ' for _ in range(field_size_x)] for _ in range(field_size_y)]

class Game:
    def __init__(self):
        self.field = create_empty_field()
        self.tick_id = None
        self.game_id = None

class Api:
    def __init__(self, token: str, url: str = "https://api.bot-games.fun/game/semaphore"):
        self.url = url
        self.headers = {'content-type': 'application/json'}
        self.token = token
        self.actions = ['join', ]
        self.game = None

    def join(self, debug: bool = False) -> [bool, str, str]:
        if 'join' not in self.actions:
            raise ValueError(f"Possible actions are {self.actions}. Trying 'join'")
        self.game = Game()
        res = req.post(self.url + '/join/v1', headers=self.headers, json={'token': self.token, 'debug': debug})
        errs = self._errors(res)
        if errs[0]:
            if(errs[0] == "AlreadyInGame"):
                self.game.game_id = errs[1]
                return True, 'AlreadyInGame', self.game.game_id

            return False, errs[0], errs[1]

        self.game.game_id = res.json()['id']
        return True, 'JoinedGame', self.game.game_id

    def wait_turn(self) -> [bool, str, str]:
        res = req.post(self.url + '/wait_turn/v1', headers=self.headers, json={'token': self.token,
                                                                               'game_id': self.game.game_id})
        errs = self._errors(res)
        if errs[0]:
            return False, errs[0], errs[1]
        res = res.json()
        self.game.field = [[color_to_letter(x) for x in row] for row in res['field']]
        self.game.tick_id = res['tick_id']
        self.actions = ['action', ]
        return True, 'WaitTurn', self.game.tick_id

    def action(self, coord: tuple[int, int]) -> [bool, str, str]:
        if 'action' not in self.actions:
            raise ValueError(f"Possible actions are {self.actions}. Trying 'action'")
        res = req.post(self.url + '/action/v1', headers=self.headers, json={'token': self.token,
                                                                          'game_id': self.game.game_id,
                                                                          'y': coord[0], 'x': coord[1]})
        errs = self._errors(res)
        if errs[0]:
            return False, errs[0], errs[1]
        return True, 'ActionAt', coord

    @staticmethod
    def _errors(res: req.Response) -> [str, str]:
        if res.status_code == 200:
            return None, None
        if res.status_code == 400:
            res = res.json()
            if res['code'][:8].lower() == 'invalid':
                raise ValueError(res['message'])
            if res['code'].lower() == 'alreadyingame':
                return 'AlreadyInGame', res['data']
            if res['code'].lower() == 'gamefinished':
                return 'GameFinished', res['data']
        if res.status_code == 500:
            raise Exception('Internal server error')
        raise Exception(f'Unknown code: {res.status_code}. Content: {res.content}')

