import search
import random
import math


ids = ["111111111", "111111111"]
passage_value = 10
heroes_values = {11, 12, 13, 14}
wall_value = 20
pit_value = 30
doors_values = {45, 46, 47, 48, 49}
keys_values = [55, 56, 57, 58, 59]
monster_value = 60
gold_value = 70

unpassable_values = {wall_value}
unpassable_values.update(doors_values)
passable_values = [passage_value, gold_value]
passable_values.extend(keys_values)

class WumpusProblem(search.Problem):
    """This class implements a wumpus problem"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        initial_state = set()
        self.doors = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        self.keys = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        for i in range(len(initial)):
            for j in range(len(initial[0])):
                if initial[i][j] in heroes_values:
                    initial_state.add((initial[i][j],i,j))
                elif initial[i][j] == gold_value:
                    self.treasure = (i, j)
                elif initial[i][j] in doors_values:
                    initial_state.add((initial[i][j], i, j))
                elif initial[i][j] in keys_values:
                    self.keys[initial[i][j] - 55] = (i, j)
                elif initial[i][j] == monster_value:
                    initial_state.add((monster_value, i, j))
        self.game_board = initial
        search.Problem.__init__(self, initial)
        self.initial = frozenset(initial_state)
        
    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        for hero_state in filter(lambda x : x[0] in heroes_values, state):
            hero_number, row, column = hero_state
            for action in self.calculate_actions(hero_number, row, column, state):
                yield action
    
    def can_kill_monster(self, hero, direction, monster):
        hero_number, row, column = hero
        if direction in ['R', 'L']:
            return row == monster[1]
        else:
            return column == monster[2]

    def shoot_action_result(self, direction, used_hero, state):
        killed_monster = next(filter(lambda x: x[0] == monster_value and self.can_kill_monster(used_hero, direction, x), state))
        new_state = set(state)
        new_state.remove(killed_monster)
        return frozenset(new_state)

    def remove_door(self, row, column, state):
        return set(filter(lambda x : x[0] != self.game_board[row][column] - 10, state))

    def kill_hero(self, hero, row, column, state):
        if (monster_value, row, column + 1) in state:
            state.remove((hero, row, column))
            state.remove((monster_value, row, column + 1))
        elif (monster_value, row, column - 1) in state:
            state.remove((hero, row, column))
            state.remove((monster_value, row, column - 1))
        elif (monster_value, row + 1, column) in state:
            state.remove((hero, row, column))
            state.remove((monster_value, row + 1, column))
        elif (monster_value, row - 1, column) in state:
            state.remove((hero, row, column))
            state.remove((monster_value, row - 1, column))

    def move_action_result(self, direction, used_hero, state):
        hero_number, row, column = used_hero
        new_state = [x for x in state if x[0] != hero_number]
        if direction == 'R':
            new_state.append((hero_number, row, column + 1))
        elif direction == 'L':
            new_state.append((hero_number, row, column - 1))
        elif direction == 'U':
            new_state.append((hero_number, row - 1, column))
        elif direction == 'D':
            new_state.append((hero_number, row + 1, column))
        hero, row, column = new_state[-1]
        new_state = self.remove_door(row, column, new_state)
        self.kill_hero(hero, row, column, new_state)
        return frozenset(new_state)

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        direction, hero, current_action = action
        used_hero = next(filter(lambda x: x[0] == hero, state))
        if current_action == 'shoot':
            return self.shoot_action_result(direction, used_hero, state)
        else :
            return self.move_action_result(direction, used_hero, state)

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

    def can_move(self, row, column, passable, state):
        return self.game_board[row][column] in passable or \
            (self.game_board[row][column] == monster_value and (monster_value, row, column) not in state)

    def calculate_monster_actions(self, row, column, hero, state):
        actions = []
        for monster in filter(lambda  x: x[0] == monster_value, state):
            value, monster_row, monster_column = monster
            if row == monster_row:
                if monster_column < column:
                    if len(unpassable_values.intersection(set(self.game_board[row][monster_column:column]))) == 0:
                        actions.append(('L', hero, 'shoot'))
                elif len(unpassable_values.intersection(set(self.game_board[row][column:monster_column]))) == 0:
                    actions.append(('R', hero, 'shoot'))
            elif column == monster_column:
                if monster_row < row:
                    if len(unpassable_values.intersection({self.game_board[monster_row + i][column] for i in range(row - monster_row)})) == 0:
                        actions.append(('U', hero, 'shoot'))
                elif len(unpassable_values.intersection({self.game_board[row + i][column] for i in range(monster_row - row)})) == 0:
                    actions.append(('D', hero, 'shoot'))
        return actions

    def calculate_actions(self, hero, row, column, state):
        ''' this function calculate the actions avialable for
        a single state(not list)
        '''
        actions = []
        #calculate monster actions
        actions.extend(self.calculate_monster_actions(row, column, hero, state))
        passable = [hero]
        passable.extend(passable_values)
        passable.extend(doors_values.symmetric_difference([x[0] for x in filter(lambda x : x[0] in doors_values, state)]))
        passable.extend(heroes_values.symmetric_difference([x[0] for x in filter(lambda x : x[0] in heroes_values, state)]))
        if len(self.game_board[0]) > column + 1 and self.can_move(row, column + 1, passable, state):
            actions.append(('R', hero, 'move'))
        if column - 1 >= 0 and self.can_move(row, column - 1, passable, state):
            actions.append(('L', hero, 'move'))
        if len(self.game_board) > row + 1 and self.can_move(row + 1, column, passable, state):
            actions.append(('D', hero, 'move'))
        if row - 1 >= 0 and self.can_move(row - 1, column, passable, state):
            actions.append(('U', hero, 'move'))

        return actions

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

def create_wumpus_problem(game):
    return WumpusProblem(game)

