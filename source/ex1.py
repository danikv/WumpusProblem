import search
import random
import math


ids = ["111111111", "111111111"]
passage_value = 10
heroes_values = [11, 12, 13, 14]
wall_value = 20
pit_value = 30
doors_values = [45, 46, 47, 48, 49]
keys_values = [55, 56, 57, 58, 59]
monster_value = 60
gold_value = 70


class WumpusProblem(search.Problem):
    """This class implements a wumpus problem"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        heroes = []
        self.doors = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        self.keys = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        for i in range(len(initial)):
            for j in range(len(initial[0])):
                if initial[i][j] in heroes_values:
                    heroes.append((initial[i][j],i,j))
                elif initial[i][j] == gold_value:
                    self.treasure = (i, j)
                elif initial[i][j] in doors_values:
                    self.doors[initial[i][j] - 45] = (i, j)
                elif initial[i][j] in keys_values:
                    self.keys[initial[i][j] - 55] = (i, j)
        self.game_board = initial
        search.Problem.__init__(self, initial)
        self.initial = frozenset(heroes)
        
    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        for hero_state in state:
            hero_number, row, column = hero_state
            for action in self._calculate_actions(hero_number, row, column, state):
                yield action
    
    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        direction, hero, current_action = action
        used_hero = filter(lambda x: x[0] == hero, state)
        not_used_heroes = [x for x in state if x[0] != hero]
        new_state = ()
        for hero in used_hero:
            hero_number, row, column = hero
            if direction == 'R':
                new_state = (hero_number, row, column + 1)
            elif direction == 'L':
                new_state = (hero_number, row, column - 1)
            elif direction == 'U':
                new_state = (hero_number, row - 1, column)
            elif direction == 'D':
                new_state = (hero_number, row + 1, column)
        not_used_heroes.append(new_state)
        print(not_used_heroes)
        return frozenset(not_used_heroes)

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
        Returns True if it is, False otherwise."""
        if state != None:
            for hero_state in state:
                if hero_state[1:] == self.treasure:
                    return True
        return False

    def _calculate_actions(self, hero, row, column, state):
        ''' this function calculate the actions avialable for
        a single state(not list)
        '''
        actions = []
        if len(self.game_board[0]) > column + 1 and self.game_board[row][column + 1] in [passage_value, gold_value]:
            actions.append(('R', hero, 'move'))
        if column - 1 >= 0 and self.game_board[row][column - 1] in [passage_value, gold_value]:
            actions.append(('L', hero, 'move'))
        if len(self.game_board) > row + 1 and self.game_board[row + 1][column] in [passage_value, gold_value]:
            actions.append(('D', hero, 'move'))
        if row - 1 >= 0 and self.game_board[row - 1][column] in [passage_value, gold_value]:
            actions.append(('U', hero, 'move'))
        return actions


    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""



def create_wumpus_problem(game):
    return WumpusProblem(game)

