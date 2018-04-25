# libraries
import sys 
from copy import deepcopy
from random import randint 

# parameters
depth = 5
mc_sim = 100

###############################

def extract_string(board_string):
    """ Extract the board state and the last move from the input string
    Args:
        board_string: the input string as specified in the guidelines
    
    Returns:
        current board state (python list), last_move (tuple(int))
    """
    
    i = 0 
    # extracting board
    board = []
    while board_string[i] != "L":
        if board_string[i] == "[":
            temp = []
        elif board_string[i] == "]":
            board.append(temp)
        else:
            temp.append(int(board_string[i]))
        i += 1

    # extracting last move 
    if board_string[i+9] == "n":
        last_move = None 
    else:
        temp_m = [int(s) for s in (board_string[i+10:i+17]).split(",")]
        last_move = tuple(temp_m)
    
    return board, last_move
    
#####################################

# class board for applying moves, determining available moves and evaluating the board.

class Board:
    
    def __init__(self, size):
        # Required to specify the size
        self.size = size
    
    def _trans(self, move):
        # returns the indices in the board_state 
        return self.size + 1 - move[1], move[2] 
    
    def _surround_colours(self, board_state, move):
        # returns a list of 6 elements consist of all colours around the move
        l = self._trans(move) 
        _1 = board_state[l[0]][l[1]-1]
        _2 = board_state[l[0]-1][l[1]-1]
        _3 = board_state[l[0]-1][l[1]]
        _4 = board_state[l[0]][l[1]+1]
        if l[0] == self.size: 
            offset = -1
        else:
            offset = 0
        _5 = board_state[l[0]+1][l[1]+1+offset]
        _6 = board_state[l[0]+1][l[1]+offset]
        return [_1, _2, _3, _4, _5, _6] 
    
    def _apply_move(self, board_state, move):
        # applies the move to board_state via reference
        l = self._trans(move)
        board_state[l[0]][l[1]] = move[0] # assign colour to passing ref 
        return None
    
    def available_moves(self, board_state, last_move):
        # Computes all the available moves given the board_state and the previous move 
        moves = []
        locations = []
        if last_move !=  None:
            if last_move[2] > 1:
                locations.append((last_move[0], last_move[1], last_move[2]-1, last_move[3]+1))
                if last_move[1] < self.size:
                    locations.append( \
                        (last_move[0], last_move[1]+1, last_move[2]-1, last_move[3]))
            if last_move[3] > 1:
                if last_move[1] < self.size:
                    locations.append( \
                        (last_move[0], last_move[1]+1, last_move[2], last_move[3]-1))
                locations.append((last_move[0], last_move[1], last_move[2]+1, last_move[3]-1))
            if last_move[1] > 1:
                locations.append((last_move[0], last_move[1]-1, last_move[2], last_move[3]+1))
                locations.append((last_move[0], last_move[1]-1, last_move[2]+1, last_move[3]))
            # print(locations)
            for s in locations:
                l = self._trans(s)
                if board_state[l[0]][l[1]] == 0:
                    for c in [1,2,3]:
                        moves.append((c,s[1],s[2],s[3]))
            # return the moves if it is non-empty 
            if len(moves) > 0:
                return moves 
                
        # all zeros are valid moves 
        for x in range(1, self.size + 1):
            for y in range(1, self.size - x + 2):
                if board_state[self.size + 1 - x][y] == 0: 
                    for c in [1,2,3]:
                        moves.append((c, x, y, self.size - x - y + 2))
        return moves 
            
    def evaluate(self, board_state, move, side):
        """ evaluate the current state via Monte Carlo methods
        Returns:
            the score of current state: an int between 0 and mc_sim 
        """
        score = 0 
        for i in range(mc_sim):
            sim_board_state = deepcopy(board_state)
            ran_move = move
            while not self.has_lost(sim_board_state, ran_move):
                #### APPLY RANDOM MOVE
                a_moves = self.available_moves(sim_board_state, ran_move)
                ran_move = a_moves[randint(0,len(a_moves)-1)]
                self._apply_move(sim_board_state, ran_move)
                side = - side
            if side > 0:
                score += 1
        return score 
                  
    def has_lost(self, board_state, move):
        """ determine if this move is a losing move
        Returns:
            Bool: True if has lost
        """
        surround = self._surround_colours(board_state, move)
        for i in range(6):
            if move[0] * surround[i-1] * surround[i] == 6:
                return True
        return False
        
#################################################

def min_max_alpha_beta(board, board_state, last_move, side, max_depth, 
                       alpha=-sys.float_info.max, beta=sys.float_info.max):
    """ Runs the minimax with alpha beta pruning 
    Inputs:
        board: Board()
        board_state: list of states
        last_move: (c, a, b)
        side (int): +1 or -1
        max_depth (int)
        alpha, beta: ignored
    Returns: 
        score, best_move
    """
    
    best_score_move = None
    
    moves = board.available_moves(board_state, last_move)
    
    # if no available moves, return tied with no moves 
    if not moves:
        return 0, None
    
    for move in moves:
        new_board_state = deepcopy(board_state) 
        board._apply_move(new_board_state, move)
        
        # if the game is lost in this move 
        if board.has_lost(new_board_state, move):
            score = - 10000 * side 
        else:
            # stopping search if depth has reached
            if max_depth <= 1:
                score = board.evaluate(new_board_state, move, -side)
            else:
                score, _ = min_max_alpha_beta(board, new_board_state, move, -side, 
                                              max_depth - 1, alpha,
                                              beta)
        if side > 0:
            if score > alpha:
                alpha = score
                best_score_move = move
        else:
            if score < beta:
                beta = score
                best_score_move = move
        if alpha >= beta:
            break

    return (alpha, best_score_move) if side > 0 else (beta, best_score_move)


################################################


if __name__ == "__main__":
    
    cur_board_state, last_move = extract_string(sys.argv[1])
    
    # New Board 
    board = Board(len(cur_board_state)-2) 
    
    best_score, best_move = min_max_alpha_beta(board, cur_board_state, last_move, +1, depth)
    
    if best_score == -10000:
        print("Lost!")
    
    print("Best move: " + str(best_move))
