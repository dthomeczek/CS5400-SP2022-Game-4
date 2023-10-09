from games.chess.movement import *
import random
import time

# Characters for all pieces to associate with a score
PIECES = ["p", "r", "n", "b", "q", "k"]

# Function to run the actual algorithm
# In this case, Iterative-Deepening Depth-Limited Min-Max
def algorithm(board_list, color, remaining_time, history):
    # Dictionary to hold moves
    move_dict = {}
    move = ""
    score = 0 # Initial score value
    start_depth = 0 # Starting depth of 0
    max_depth = 100 # Cap depth
    taken = 0

    alpha = -99999999999
    beta = 99999999999

    max_time = 900
    quiescent_lim = 2
    history_table = []

    limited_time = (estimated_time(history, remaining_time, max_time))

    for depth in range(0, max_depth):
        start_time = time.time()
        if max_depth == 0:
            action_list = actions(color, board_list)
            move_dict = get_score(board_list, action_list)
            score, move = set_min_max(move_dict, start_depth)

        action_list = min_max(board_list, color, move, score, alpha, beta, history_table, False, quiescent_lim, start_depth, depth)

        elapsed = time.time() - start_time
        taken = taken + elapsed

        if ((5 * taken) > limited_time):
            break
    return action_list

# Performs the min max part of the algorithm
def min_max(board_list, color, parent, score, alpha, beta, history_table, is_quiescent, quiescent_lim, depth, max_depth):
    selected = () # Tuple for the selected move and score
    move_dict = {} # Dictionary for the moves
    best_choices = {} # Dictionary for the best choices among moves found in time limit
    h_val = 0 # Heuristic value

    # Determines player and enemy color
    if (color == "white"):
        enemy = "black"
    else:
        enemy = "white"
    
    if (depth == max_depth and is_quiescent):
        quiescent_lim = quiescent_lim - 1

    # If max depth reached, return score and parent
    if (depth == max_depth and not (is_quiescent and quiescent_lim >= 0)):
        return (score, parent)

    # Gets a list of valid actions
    action_list = actions(color, board_list)

    # If no actions are possible, return the score and parent
    if len(action_list) == 0:
        return (score, parent)

    # Update the scores for the moves
    move_dict = get_score(board_list, action_list)

    # Checks each action and generates a state based on that move
    for action in action_list:
        
        new_board = next_move(board_list, action, color == "white")

        for key, values in move_dict.items(): 
            if action in values:
                move_score = key
                break

        is_quiescent = quiescent(action_list, board_list)
        
        # Gets the move(s) that can follow from the current one
        if (depth == max_depth):
            child_move = min_max(new_board, enemy, action_list, score, alpha, beta, history_table, is_quiescent, quiescent_lim, depth, max_depth)
        else:
            child_move = min_max(new_board, enemy, action_list, score, alpha, beta, history_table, is_quiescent, quiescent_lim, depth + 1, max_depth)

        # Applies a heuristic value to assess best move options
        h_val = h(depth, move_score, child_move[0])

        # Used to determine which player is currently moving, the user or the opponent
        if depth % 2 == 0:
            alpha = max(alpha, h_val)
        else:
            beta = min(beta, h_val)

        if beta <= alpha:
            return (h_val, action)

        # Appends the move dictionary, or empties it if the heuristic is not present
        if h_val not in best_choices:
            best_choices[h_val] = []
        best_choices[h_val] = best_choices[h_val] + [action]

    # Get the selected move from the move dictionary at a specified depth
    selected = set_min_max(best_choices, depth)

    best_choices = {}

    best_choices[selected[0]] = [selected[1]]
    return selected

# Gets the score for all possible moves
def get_score(board_list, action_list):
    PIECE_VALS = {"p": 1, "n":3, "b": 3, "r": 5, "q": 9, "k": 10} # Scores by piece
    move_scores = {} # Holds the scores
    for action in action_list:
        # Converts the given move to coordinates
        move = uci_to_coords(action)
        cap_val = 0 # Value of a capture (0 if none captured)
        piece = board_list.board[move[2]][move[3]]

        # Checks through the pieces and their values to assess each piece
        # and assign a score based on if said piece is taken
        if piece.lower() in PIECES:
            cap_val = PIECE_VALS[piece.lower()]
            if cap_val not in move_scores:
                move_scores[cap_val] = []
            move_scores[cap_val] = move_scores[cap_val] + [action]
        elif piece == ".":
            if cap_val not in move_scores:
                move_scores[cap_val] = []
            move_scores[cap_val] = move_scores[cap_val] + [action]

    return move_scores

# Heuristic function that determines whether a move will result in a gain to the player or not
def h(depth, parent, child):
    gain = 0
    if depth % 2 == 0:
        gain = child + parent
    else:
        gain = child - parent
    return gain

# Sets the min max values
def set_min_max(move_scores, depth):
    score = 0
    move = ""

    if depth % 2 == 0:
        score = max(move_scores)
    else:
        score = min(move_scores)
    
    # Gets a list of all moves with a given score (best score)
    moves_with_score = move_scores[score]

    # If multiple moves have the same score (best score), picks a move among those 
    # with the same score and runs with it, otherwise takes the best score
    if len(moves_with_score) > 1:
        move = random.choice(moves_with_score)
    else:
        move = moves_with_score[0]

    return (score, move)

# Gets the time to complete a turn
def estimated_time(history, remaining_time, max_time):
    avg_moves = 50 # Basing on an average of a 50 turn game
    start_time = time.time()
    moves_made = round(len(history) / 2)
    if moves_made <= 10: # Early game moves
        alloted_time = max_time / (2 * avg_moves)
    elif moves_made <= 30: # Midgame moves
        alloted_time = remaining_time * (1 / avg_moves)
    else: # Endgame moves
        alloted_time = remaining_time * (1 / (2 * avg_moves))
    
    elapsed = time.time() - start_time
    alloted_time = alloted_time - elapsed
    return alloted_time

# Function for quiescent search, returns true if state is non-quiescence
# and false if state is quiescence
def quiescent(move, board_list):
    move_dict = get_score(board_list, move)
    for key in move_dict:
        move_score = key
    
    if move_score >= 3:
        return True
    return False

# Adds the next move to be made to the history table
def add_history(history_table, board_list, move):
    for list in history_table:
        if list[0] == board_list.board:
            if list[1] == move:
                index_val = history_table.index(list)
                history_table[index_val][2] = history_table[index_val][2] + 1
                return
    board_list.board = [x[:] for x in board_list.board]
    history_table.append([board_list.board, move, 1])

# Used to find a value within the history table
def find_history(history_table, board_list, move):
    for list in history_table:
        if list[0] == board_list.board:
            if list[1] == move:
                index_val = history_table.index(list)
                return history_table[index_val][2]
    return 0