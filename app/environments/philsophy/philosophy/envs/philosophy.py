# Adapted from https://mblogscode.com/2016/06/03/python-naughts-crossestic-tac-toe-coding-unbeatable-ai/

import gym
import numpy as np

import config

from stable_baselines import logger


class Player():
    def __init__(self, id, token):
        self.id = id
        self.token = token


class Token():
    def __init__(self, symbol, number):
        self.number = number
        self.symbol = symbol




class PhilosophyEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, verbose = False, manual = False):
        super(PhilosophyEnv, self).__init__()
        self.name = 'philosophy'
        self.manual = manual

        self.grid_length = 7
        self.n_players = 2

        self.tiles = gym.spacs.Dict({
            0: gym.spaces.Dict({
                "target": np.array([0, 1]),
                "moveVector": np.array([0, 1])
               }),
            1: gym.spaces.Dict({
                "target": np.array([1, 1]),
                "moveVector": np.array([1, 1])
               }),
            2: gym.spaces.Dict({
                "target": np.array([0, 1]),
                "moveVector": np.array([-1, 0])
               }),
            3: gym.spaces.Dict({
                "target": np.array([0, 1]),
                "moveVector": np.array([1, 0])
               }),
            4: gym.spaces.Dict({
                "target": np.array([0, 1]),
                "moveVector": np.array([-1, -1])
               }),
            5: gym.spaces.Dict({
                "target": np.array([0, 1]),
                "moveVector": np.array([1, -1])
               }),
            6: gym.spaces.Dict({
                "target": np.array([0, 2]),
                "moveVector": np.array([0, 1])
               }),
            7: gym.spaces.Dict({
                "target": np.array([2, 2]),
                "moveVector": np.array([1, 1])
               }),
            8: gym.spaces.Dict({
                "target": np.array([2, 2]),
                "specialAction": 2
               }),
            9: gym.spaces.Dict({
                "target": np.array([0, 1]),
               }),
            10: gym.spaces.Dict({
                "target": np.array([0, 1]),
               }),
            11: gym.spaces.Dict({
                "target": np.array([1, 1]),
                "specialAction": 4
               }),
        })

        self.num_squares = self.grid_length * self.grid_length
        self.grid_shape = (self.grid_length, self.grid_length)

        self.tile_board = np.array([])

        # x, y, orientation clockwise, tiletype, special action (turning or chosing move)
        self.action_space = gym.spaces.Box(
            -3, 11,
            shape=(5, 5, 3, 2),
            dtype=np.int8
        )

        # x, y, orientation clockwise, tiletype, own tile(1)/ opponent(2),
        self.observation_space = gym.spaces.Box(
            -3, 11,
            shape=(7, 7, 4),
            dtype=np.int8
        )
        self.verbose = verbose
        self.available_tiles = [set(range(0, 12)), set(range(0, 12))]
        self.current_player_num = 1


    @property
    def observation(self):
        return self.observation_space

    @property
    def legal_actions(self):
        legal_actions = []

        for x in range(self.grid_length):
            for y in range(self.grid_length):
                # Skip tiles outside the 3x3 center
                if x < 2 or x > 4 or y < 2 or y > 4:
                    continue

                # If field busy, try next
                if self.tile_board[x][y][2] != 0:
                    continue

                for tile in self.available_tiles:
                    for orientation in range(4):
                        for special_action in range(self.tiles[tile]["specialAction"] if "specialAction" in self.tiles[tile] else 1):
                            legal_actions.append([x, y, orientation, tile, special_action])

        return np.array(legal_actions)


    def check_game_over(self):

        winner = 0

        for moving_x in range(3, self.grid_length):
            same_owner = 1
            last_owner = 0

            for x, y in zip(range(moving_x, self.grid_length),range(self.grid_length)):
                if self.tile_board[x][y][3] == last_owner and last_owner != 0:
                    same_owner += 1

                    if same_owner == 3:
                        winner = last_owner
                else:
                    last_owner = 0
                    same_owner = 1




        # check game over
        for i in range(self.grid_length):
            # horizontals and verticals
            if ((self.square_is_player(i*self.grid_length,current_player_num) and self.square_is_player(i*self.grid_length+1,current_player_num) and self.square_is_player(i*self.grid_length+2,current_player_num))
                or (self.square_is_player(i+0,current_player_num) and self.square_is_player(i+self.grid_length,current_player_num) and self.square_is_player(i+self.grid_length*2,current_player_num))):
                return  1, True

        # diagonals
        if((self.square_is_player(0,current_player_num) and self.square_is_player(4,current_player_num) and self.square_is_player(8,current_player_num))
            or (self.square_is_player(2,current_player_num) and self.square_is_player(4,current_player_num) and self.square_is_player(6,current_player_num))):
                return  1, True

        if self.turns_taken == self.num_squares:
            logger.debug("Board full")
            return  0, True

        return 0, False

    @property
    def current_player(self):
        return self.players[self.current_player_num]


    def step(self, action):


        self.tile_board


        reward = [0,0]



        # check move legality
        board = self.board

        if (board[action].number != 0):  # not empty
            done = True
            reward = [1, 1]
            reward[self.current_player_num] = -1
        else:
            board[action] = self.current_player.token
            self.turns_taken += 1
            r, done = self.check_game_over()
            reward = [-r,-r]
            reward[self.current_player_num] = r

        self.done = done

        if not done:
            self.current_player_num = (self.current_player_num + 1) % 2

        return self.observation, reward, done, {}

    def reset(self):
        self.board = [Token('.', 0)] * self.num_squares
        self.players = [Player('1', Token('X', 1)), Player('2', Token('O', -1))]
        self.current_player_num = 0
        self.turns_taken = 0
        self.done = False
        logger.debug(f'\n\n---- NEW GAME ----')
        return self.observation


    def render(self, mode='human', close=False, verbose = True):
        logger.debug('')
        if close:
            return
        if self.done:
            logger.debug(f'GAME OVER')
        else:
            logger.debug(f"It is Player {self.current_player.id}'s turn to move")

        logger.debug(' '.join([x.symbol for x in self.board[:self.grid_length]]))
        logger.debug(' '.join([x.symbol for x in self.board[self.grid_length:self.grid_length*2]]))
        logger.debug(' '.join([x.symbol for x in self.board[(self.grid_length*2):(self.grid_length*3)]]))

        if self.verbose:
            logger.debug(f'\nObservation: \n{self.observation}')

        if not self.done:
            logger.debug(f'\nLegal actions: {[i for i,o in enumerate(self.legal_actions) if o != 0]}')


    def rules_move(self):
        if self.current_player.token.number == 1:
            b = [x.number for x in self.board]
        else:
            b = [-x.number for x in self.board]

        # Check computer win moves
        for i in range(0, self.num_squares):
            if b[i] == 0 and testWinMove(b, 1, i):
                logger.debug('Winning move')
                return self.create_action_probs(i)
        # Check player win moves
        for i in range(0, self.num_squares):
            if b[i] == 0 and testWinMove(b, -1, i):
                logger.debug('Block move')
                return self.create_action_probs(i)
        # Check computer fork opportunities
        for i in range(0, self.num_squares):
            if b[i] == 0 and testForkMove(b, 1, i):
                logger.debug('Create Fork')
                return self.create_action_probs(i)
        # Check player fork opportunities, incl. two forks
        playerForks = 0
        for i in range(0, self.num_squares):
            if b[i] == 0 and testForkMove(b, -1, i):
                playerForks += 1
                tempMove = i
        if playerForks == 1:
            logger.debug('Block One Fork')
            return self.create_action_probs(tempMove)
        elif playerForks == 2:
            for j in [1, 3, 5, 7]:
                if b[j] == 0:
                    logger.debug('Block 2 Forks')
                    return self.create_action_probs(j)
        # Play center
        if b[4] == 0:
            logger.debug('Play Centre')
            return self.create_action_probs(4)
        # Play a corner
        for i in [0, 2, 6, 8]:
            if b[i] == 0:
                logger.debug('Play Corner')
                return self.create_action_probs(i)
        #Play a side
        for i in [1, 3, 5, 7]:
            if b[i] == 0:
                logger.debug('Play Side')
                return self.create_action_probs(i)


    def create_action_probs(self, action):
        action_probs = [0.01] * self.action_space.n
        action_probs[action] = 0.92
        return action_probs


def checkWin(b, m):
    return ((b[0] == m and b[1] == m and b[2] == m) or  # H top
            (b[3] == m and b[4] == m and b[5] == m) or  # H mid
            (b[6] == m and b[7] == m and b[8] == m) or  # H bot
            (b[0] == m and b[3] == m and b[6] == m) or  # V left
            (b[1] == m and b[4] == m and b[7] == m) or  # V centre
            (b[2] == m and b[5] == m and b[8] == m) or  # V right
            (b[0] == m and b[4] == m and b[8] == m) or  # LR diag
            (b[2] == m and b[4] == m and b[6] == m))  # RL diag


def checkDraw(b):
    return 0 not in b

def getBoardCopy(b):
    # Make a duplicate of the board. When testing moves we don't want to
    # change the actual board
    dupeBoard = []
    for j in b:
        dupeBoard.append(j)
    return dupeBoard

def testWinMove(b, mark, i):
    # b = the board
    # mark = 0 or X
    # i = the square to check if makes a win
    bCopy = getBoardCopy(b)
    bCopy[i] = mark
    return checkWin(bCopy, mark)


def testForkMove(b, mark, i):
    # Determines if a move opens up a fork
    bCopy = getBoardCopy(b)
    bCopy[i] = mark
    winningMoves = 0
    for j in range(0, 9):
        if testWinMove(bCopy, mark, j) and bCopy[j] == 0:
            winningMoves += 1
    return winningMoves >= 2
