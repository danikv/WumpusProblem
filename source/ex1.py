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
        #find goal
        self.game_board = initial
        self.heroes = []
        self.doors = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        self.keys = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        for i in range(len(initial)):
            for j in range(len(initial[0])):
                if initial[i][j] in heroes_values:
                    self.heroes.append((i,j))
                elif initial[i][j] == gold_value:
                    self.goal = gold_value
                elif initial[i][j] in doors_values:
                    self.doors[initial[i][j] - 45] = (i, j)
                elif initial[i][j] in keys_values:
                    self.keys[initial[i][j] - 55] = (i, j)
        self.initial = 0
        search.Problem.__init__(self, initial)
        
    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        actions = []

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""


    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        return 0


    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""



def create_wumpus_problem(game):
    return WumpusProblem(game)

