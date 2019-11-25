import search
import random
import math
from collections import defaultdict
import sys

ids = ["111111111", "111111111"]

class Graph:
  def __init__(self):
    self.nodes = set()
    self.edges = defaultdict(list)
    self.distances = {}

  def add_node(self, value):
    self.nodes.add(value)

  def add_edge(self, from_node, to_node, distance):
    self.edges[from_node].append(to_node)
    self.edges[to_node].append(from_node)
    self.distances[(from_node, to_node)] = distance
    self.distances[(to_node, from_node)] = distance

passage_encoding = 10
heroes_encoding = {11, 12, 13, 14}
doors_encoding = {45, 46, 47, 48, 49}
keys_encoding = [55, 56, 57, 58, 59]
monster_encoding = 60
gold_encoding = 70

class WumpusProblem(search.Problem):
    """This class implements a wumpus problem"""

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        game_distances = [[0 for i in range(len(initial[0]))] for j in range(len(initial))]
        state = set()
        self.doors = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        self.keys = [(0,0), (0,0), (0,0), (0,0), (0,0)]
        self.monsters = set()
        self.can_move = []
        self.can_move.extend(keys_encoding)
        self.can_move.append(gold_encoding)
        self.can_move.append(passage_encoding)
        self.cant_move = set()
        self.cant_move.update(doors_encoding)
        #add wall
        self.cant_move.add(20)
        self.init(game_distances, state, initial)
        self.game = initial
        self.calculateHeuristic(game_distances)
        search.Problem.__init__(self, initial)
        self.initial = frozenset(state)

    def init(self, game_distances, state, initial):
        for i in range(len(initial)):
            for j in range(len(initial[0])):
                if initial[i][j] in heroes_encoding:
                    state.add((initial[i][j],i,j))
                    game_distances[i][j] = 1
                elif initial[i][j] == monster_encoding:
                    state.add((monster_encoding, i, j))
                    self.monsters.add((i,j))
                    game_distances[i][j] = sys.maxsize
                elif initial[i][j] in doors_encoding:
                    state.add((initial[i][j], i, j))
                    self.doors[initial[i][j] - 45] = (i, j)
                    game_distances[i][j] = sys.maxsize
                elif initial[i][j] == gold_encoding:
                    self.gold = (i, j)
                    game_distances[i][j] = 1
                elif initial[i][j] in keys_encoding:
                    self.keys[initial[i][j] - 55] = (i, j)
                    game_distances[i][j] = 1
                elif initial[i][j] == passage_encoding:
                    game_distances[i][j] = 1
                else:
                    game_distances[i][j] = sys.maxsize
    
    def createGraph(self, graph, game_distances):
        for row in range(len(game_distances)):
            for column in range(len(game_distances[0])):
                graph.add_node((row, column))
                addGraphEdge(graph, game_distances, row, column, row, column + 1, lambda row,column: game_distances[row][column])
                addGraphEdge(graph, game_distances, row, column, row, column - 1, lambda row,column: game_distances[row][column])
                addGraphEdge(graph, game_distances, row, column, row + 1, column, lambda row,column: game_distances[row][column])
                addGraphEdge(graph, game_distances, row, column, row - 1, column, lambda row,column: game_distances[row][column])
        for i in range(len(self.keys)):
            if self.keys[i] != (0,0) and self.doors[i] != (0,0):
                graph.add_edge(self.keys[i], self.doors[i], 0)
                #update near door values
                row, column = self.doors[i]
                addGraphEdge(graph, game_distances, row, column, row, column + 1, lambda x,y : 1)
                addGraphEdge(graph, game_distances, row, column, row, column - 1, lambda x,y : 1)
                addGraphEdge(graph, game_distances, row, column, row + 1, column, lambda x,y : 1)
                addGraphEdge(graph, game_distances, row, column, row - 1, column, lambda x,y : 1)
        for monster in self.monsters:
            monster_row, monster_column = monster
            for i in range(1, monster_column):
                if not addMonsterEdge(graph, self.game, monster_row, monster_column, monster_row, monster_column - i, self.cant_move, i):
                    break
            for i in range(1, len(self.game[0]) - monster_column):
                if not addMonsterEdge(graph, self.game, monster_row, monster_column, monster_row, monster_column + i, self.cant_move, i):
                    break
            for i in range(1, monster_row):
                if not addMonsterEdge(graph, self.game, monster_row, monster_column, monster_row + i, monster_column, self.cant_move, i):
                    break
            for i in range(1, len(self.game) - monster_row):
                if not addMonsterEdge(graph, self.game, monster_row, monster_column, monster_row - i, monster_column, self.cant_move, i):
                    break
        
    def calculateHeuristic(self, game_distances):
        #create graph
        graph = Graph()
        self.createGraph(graph, game_distances)
        #calculate distance from gold
        weights, _ = dijsktra(graph, self.gold)
        self.shortest_path_heuristic = weights

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        for hero_state in filter(lambda x : x[0] in heroes_encoding, state):
            hero_number, row, column = hero_state
            for action in self.calculate_actions(hero_number, row, column, state):
                yield action

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        direction, hero, current_action = action
        used_hero = next(filter(lambda x: x[0] == hero, state))
        if current_action == 'shoot':
            return shootResult(direction, used_hero, state)
        else :
            return moveResult(self.game, direction, used_hero, state)

    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        heroes = list(filter(lambda x : x[0] in heroes_encoding, node.state))
        if len(heroes) == 0:
            return sys.maxsize
        return min(map(lambda x : self.shortest_path_heuristic[(x[1], x[2])], heroes))

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
        Returns True if it is, False otherwise."""
        if state != None:
            for hero_state in filter(lambda x : x[0] in heroes_encoding, state):
                if hero_state[1:] == self.gold:
                    return True
        return False

    def calculate_actions(self, hero, row, column, state):
        ''' this function calculate the actions avialable for
        a single state(not list)
        '''
        actions = []
        can_move_extended = [hero]
        can_move_extended.extend(self.can_move)
        can_move_extended.extend(doors_encoding.symmetric_difference([x[0] for x in filter(lambda x : x[0] in doors_encoding, state)]))
        can_move_extended.extend(heroes_encoding.symmetric_difference([x[0] for x in filter(lambda x : x[0] in heroes_encoding, state)]))
        actions.extend(moveActions(self.game, hero, row, column, state, can_move_extended))
        actions.extend(shootActions(self.game, row, column, hero, state, self.cant_move))
        return actions

    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

def isAbleToKill(hero, direction, monster):
    _, row, column = hero
    if direction == 'R':
        return row == monster[1] and column < monster[2]
    elif direction == 'L':
        return row == monster[1] and column > monster[2]
    elif direction == 'U':
        return column == monster[2] and row > monster[1]
    return column == monster[2] and row < monster[1]

def shootResult(direction, used_hero, state):
    killed_monster = next(filter(lambda x: x[0] == monster_encoding and isAbleToKill(used_hero, direction, x), state))
    new_state = set(state)
    new_state.remove(killed_monster)
    return frozenset(new_state)

def removeDoor(game, row, column, state):
    return set(filter(lambda x : x[0] != game[row][column] - 10, state))

def removeMonsterAndHeroIfInState(hero, row, column, monster_row, monster_column, state):
    if (monster_encoding, monster_row, monster_column) in state:
        state.remove((hero, row, column))
        state.remove((monster_encoding, monster_row, monster_column))
        return True
    return False

def killHero(hero, row, column, state):
    if removeMonsterAndHeroIfInState(hero, row, column, row, column + 1, state):
        return
    elif removeMonsterAndHeroIfInState(hero, row, column, row, column - 1, state):
        return
    elif removeMonsterAndHeroIfInState(hero, row, column, row + 1, column, state):
        return
    removeMonsterAndHeroIfInState(hero, row, column, row - 1, column, state)

def moveResult(game, direction, used_hero, state):
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
    new_state = removeDoor(game, row, column, new_state)
    killHero(hero, row, column, new_state)
    return frozenset(new_state)

def canMove(game, row, column, passable, state):
    return game[row][column] in passable or \
        (game[row][column] == monster_encoding and (monster_encoding, row, column) not in state)

def shootActions(game, row, column, hero, state, cant_move):
    actions = []
    for monster in filter(lambda  x: x[0] == monster_encoding, state):
        _, monster_row, monster_column = monster
        if row == monster_row:
            if monster_column < column:
                if len(cant_move & set(game[row][monster_column:column])) == 0:
                    actions.append(('L', hero, 'shoot'))
            elif len(cant_move & set(game[row][column:monster_column])) == 0:
                actions.append(('R', hero, 'shoot'))
        elif column == monster_column:
            if monster_row < row:
                if len(cant_move & {game[monster_row + i][column] for i in range(row - monster_row)}) == 0:
                    actions.append(('U', hero, 'shoot'))
            elif len(cant_move & {game[row + i][column] for i in range(monster_row - row)}) == 0:
                actions.append(('D', hero, 'shoot'))
    return actions

def moveAction(game, hero, row, column, state, can_move, actions, direction):
    if len(game) > row and len(game[0]) > column and row >= 0 and column >= 0 and canMove(game, row, column, can_move, state):
        actions.append((direction, hero, 'move'))

def moveActions(game, hero, row, column, state, can_move):
    actions = []
    moveAction(game, hero, row + 1, column, state, can_move, actions, 'D')
    moveAction(game, hero, row - 1, column, state, can_move, actions, 'U')
    moveAction(game, hero, row, column + 1, state, can_move, actions, 'R')
    moveAction(game, hero, row, column - 1, state, can_move, actions, 'L')
    return actions

def getMinNode(nodes, visited):
    min_node = None
    for node in nodes:
      if node in visited:
        if min_node is None:
          min_node = node
        elif visited[node] < visited[min_node]:
          min_node = node
    return min_node

def dijsktra(graph, initial):
  visited = {initial: 0}
  path = {}

  nodes = set(graph.nodes)

  while nodes: 
    min_node = getMinNode(nodes, visited)
    if min_node is None:
      break

    nodes.remove(min_node)
    current_weight = visited[min_node]

    for edge in graph.edges[min_node]:
      weight = current_weight + graph.distances[(min_node, edge)]
      if edge not in visited or weight < visited[edge]:
        visited[edge] = weight
        path[edge] = min_node

  return visited, path

def addGraphEdge(graph, game_distances, source_row, source_column, row, column, evaluate_value):
    if len(game_distances) > row and len(game_distances[0]) > column and row >= 0 and column >= 0:
        graph.add_edge((source_row, source_column), (row, column), evaluate_value(row, column))

def addMonsterEdge(graph, game, monster_row, monster_column, current_row, current_column, cant_move, value):
    if game[current_row][current_column] not in cant_move:
        graph.add_edge((monster_row, monster_column), (current_row, current_column), value)
        return True
    return False

def create_wumpus_problem(game):
    return WumpusProblem(game)

