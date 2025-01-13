import random
import sys


VERSION = "1.0"
# 0000 => 0    empty sqare
# 0001 => 1    black stone
# 0010 => 2    white stone
# 0100 => 4    stone marker
# 0111 => 7    offboard square
# 1000 => 8    liberty marker
#
# 0101 => 5    black stone marked
# 0110 => 6    white stone marked

# 9x9 GO board
board_9x9 = []
board_9x9.extend([7] * 11)  # First row
for _ in range(9):
    board_9x9.extend([7] + [0] * 9 + [7])  # Rows with 0s in the middle
board_9x9.extend([7] * 11)  # Last row

# 13x13 GO board
board_13x13 = []
board_13x13.extend([7] * 15)  # First row
for _ in range(13):
    board_13x13.extend([7] + [0] * 13 + [7])  # Rows with 0s in the middle
board_13x13.extend([7] * 15)  # Last row

# 19x19 GO board
board_19x19 = []
board_19x19.extend([7] * 21)  # First row
for _ in range(19):
    board_19x19.extend([7] + [0] * 19 + [7])  # Rows with 0s in the middle
board_19x19.extend([7] * 21)  # Last row

MODE = "e" # m , h

# boards lookup
BOARDS = {"9": board_9x9, "13": board_13x13, "19": board_19x19}

# stones
EMPTY = 0
BLACK = 1
WHITE = 2
MARKER = 4
OFFBOARD = 7
LIBERTY = 8

# count
liberties = []
block = []

# current board used initialization
board = BOARDS[str(9)]

# GO ban size
BOARD_WIDTH = 0
BOARD_RANGE = 1  # 0
MARGIN = 2

# file markers
files = "     a b c d e f g h j k l m n o p q r s t"

# ASCII representation of stones
pieces = ".#o  bw +"

def eprint(*args, **kwargs):
    print(*args, file = sys.stderr, **kwargs)

def print_board():
    # loop over board rows
    for row in range(BOARD_RANGE):
        # loop over board columns
        for col in range(BOARD_RANGE):
            # init square
            square = row * BOARD_RANGE + col

            # init stone
            stone = board[square]

            # print rank
            if col == 0 and 0 < row < BOARD_RANGE - 1:
                rank = BOARD_RANGE - 1 - row
                print(("  " if rank < 10 else " ") + str(rank), end="")

            # print board square's content
            print(pieces[stone] + " ", end="")

        # print new line
        print()

    # print column markers
    print(files[0 : BOARD_RANGE * 2] + "\n")


# set Go ban size
def set_board_size(command):
    # hook global variables
    global BOARD_WIDTH, BOARD_RANGE, board

    size = int(command.split()[-1])
    if size not in [9, 13, 19]:
        print("? board size not supported\n")
        return -1
    # calculate current board size
    BOARD_WIDTH = size  # 9
    BOARD_RANGE = BOARD_WIDTH + MARGIN  # 11
    board = BOARDS[str(size)]
    return 0


# count liberties, saves a stone's group positions
def count_liberties(square, color):
    # init piece
    piece = board[square]

    # skip offboard squares
    if piece == OFFBOARD:
        return

    # if there's a stone at square
    if piece and piece & color and (piece & MARKER) == 0:
        # save stone's coordinate
        block.append(square)

        # mark the stone
        board[square] |= MARKER

        # look for neighbors recursively
        count_liberties(square - BOARD_RANGE, color)  # walk up
        count_liberties(square - 1, color)  # walk left
        count_liberties(square + BOARD_RANGE, color)  # walk down
        count_liberties(square + 1, color)  # walk right

    # if the square is empty
    elif piece == EMPTY:
        # mark liberty
        board[square] |= LIBERTY
        # save liberty
        liberties.append(square)


# remove captured stones
def clear_block():
    for captured in block:
        board[captured] = EMPTY


def clear_list():
    # hook global variables
    global block, liberties
    # clear block and liberties lists
    block = []
    liberties = []


# restore the board after counting stones
def restore_board():
    clear_list()
    # unmark stones
    for square in range(BOARD_RANGE * BOARD_RANGE):
        # restore piece if the square is on board
        if board[square] != OFFBOARD:
            board[square] &= 3


def clear_board():
    clear_list()

    for square in range(len(board)):
        if board[square] != OFFBOARD:
            board[square] = 0

def captures(color):
    for square in range(len(board)):
        piece = board[square]
        # skip offboard squares
        if piece == OFFBOARD: continue
        # same color
        if piece & color:
            # count liberties
            count_liberties(square, color)
            # if no liberties then remove the stones
            if len(liberties) == 0: clear_block()
            # restore the board
            restore_board()


# main loop
"""
def main():    
    set_board_size(19)  # 82 32 44
    print_board()

    count_liberties(44, BLACK)
    print_board()
    print('block:', block)
    print('liberties:', liberties)

    restore_board()
    print_board()
    print('block:', block)
    print('liberties:', liberties)
"""
column_mapping = {
    "XX": 0,
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4,
    "E": 5,
    "F": 6,
    "G": 7,
    "H": 8,
    "J": 9,
    "K": 10,
    "L": 11,
    "M": 12,
    "N": 13,
    "O": 14,
    "P": 15,
    "Q": 16,
    "R": 17,
    "S": 18,
    "T": 19,
}
reverse_column_mapping = {v: k for k, v in column_mapping.items()}


def get_board_index(position):
    column = position[0]
    row = int(position[1:])
    # print(f'row: {row}')
    col_index = column_mapping[column]
    row_index = BOARD_RANGE - 1 - row  # because of the border and reverse ordering
    return row_index * BOARD_RANGE + col_index


def get_position_from_index(index):
    if index == 0:
        return "XX"
    row_index = index // BOARD_RANGE
    col_index = index % BOARD_RANGE
    column = reverse_column_mapping[col_index]
    row = BOARD_RANGE - (row_index + 1)  # reverse row ordering and adjust for border
    return f"{column}{row}"

def set_move(square,color):
    board[square] = color
    # handle capture of opposite color
    captures(3 - color)

def play(command):
    square = get_board_index(command.split()[2])
    color = WHITE if command.split()[1] == "W" else BLACK
    set_move(square, color)


def make_random_move(color):
    square = random.randrange(BOARD_RANGE, len(board) - BOARD_RANGE - 1)
    while board[square] != 0:
        square = random.randrange(BOARD_RANGE, len(board) - BOARD_RANGE - 1)

    if BOARD_RANGE < square < len(board) - BOARD_RANGE:
        set_move(square, color)
    else:
        make_random_move(color)
    
    #count liberties
    count_liberties(square,color)
    # check for suicide move
    if len(liberties) == 0:
        restore_board()
        #take off the stone
        board[square] = EMPTY
        # search another move
        try:
            return make_random_move(color)
        except:
            return ''
        
    restore_board()
    eprint("random move", get_position_from_index(square))
    return get_position_from_index(square)


def print_board_num():
    for row in range(BOARD_RANGE):
        for col in range(BOARD_RANGE):
            print(f"{board[row * BOARD_RANGE + col]} ", end="")
        print()
        

def detect_edge(target_square):
    # checks in 4 direction for edge
    for direction in [BOARD_RANGE, 1, -BOARD_RANGE, -1]:
        if board[target_square + direction] == OFFBOARD:
            return 1
    return 0

def evaluate_best_liberty(color):
    best_count = 0
    best_liberty = liberties[0]
    # loop to find which has the most liberties
    old_liberties = liberties
    for liberty in old_liberties:
        # putting own stone and checking the count of liberty
        board[liberty] = color
        count_liberties(liberty,color)
        if len(liberties) > best_count and not detect_edge(liberty):
            best_count = len(liberties)
            best_liberty = liberty
        
        restore_board()
        board[liberty] = EMPTY
        
    return best_liberty

# fuzzy 
def membership_liberties(liberties_count):
    if liberties_count <= 1:
        return 1.0  # High risk
    elif liberties_count <= 2:
        return 0.5  # Moderate risk
    else:
        return 0.0  # Low risk

def membership_distance_to_edge(distance):
    if distance == 0:
        return 1.0  # High risk
    elif distance == 1:
        return 0.5  # Moderate risk
    else:
        return 0.0  # Low risk

def membership_group_size(group_size):
    if group_size == 1:
        return 1.0  # Small group (high risk)
    elif group_size <= 3:
        return 0.5  # Medium group
    else:
        return 0.0  # Large group (low risk)

def defuzzify(risk_values):
    total_risk = sum(risk_values)
    if total_risk > 2:
        return "defensive"
    elif total_risk > 1:
        return "balanced"
    else:
        return "aggressive"

def genmove(color):
    
    best_move = None
    best_risk_value = float("inf")
    move_type = "random"

    # Analyze the board and evaluate each possible move
    for square in range(len(board)):
        if board[square] == EMPTY:
            # Simulate placing a stone
            set_move(square, color)

            # Analyze the result
            count_liberties(square, color)
            liberties_count = len(liberties)
            group_size = len(block)
            distance = detect_edge(square)

            # Fuzzify inputs
            liberty_risk = membership_liberties(liberties_count)
            edge_risk = membership_distance_to_edge(distance)
            group_risk = membership_group_size(group_size)

            # Aggregate risks
            risk_values = [liberty_risk, edge_risk, group_risk]
            overall_risk = sum(risk_values)

            # Evaluate the move based on overall risk
            if overall_risk < best_risk_value:
                best_risk_value = overall_risk
                best_move = square
                move_type = defuzzify(risk_values)

            # Restore board to previous state
            restore_board()
            board[square] = EMPTY

    if best_move is not None:
        set_move(best_move, color)
        eprint(f"Best move {get_position_from_index(best_move)} as {move_type}")
        return get_position_from_index(best_move)
    
    # Fallback to random move if no suitable move found
    return make_random_move(color)


def score():
    return "none"


# GTP communication protocol
def gtp():
    # main GTP loop
    while True:
        # accept GUI command
        command = input()
        # handle commands
        if "name" in command:
            print("= Go\n")
        elif "protocol_version" in command:
            print("= 1\n")
        elif "version" in command:
            print("=", VERSION, "\n")
        elif "list_commands" in command:
            print("= protocol_version\n")
        elif "boardsize" in command:
            # splits the input 'boardsize 9'.
            set_board_size(command)
            print(f"={command.split()[-1]}\n")
        elif "showboard" in command:
            print("=")
            print_board()
        elif "clear_board" in command:
            clear_board()
            print("=\n")
        elif "play " in command:
            if command.split()[2] == "pass":
                sys.exit()
            play(command)
            # square = get_board_index(command.split()[2])
            # board[square] = WHITE if command.split()[1] == "W" else BLACK
            print(f"= {command.split()[-1]}\n")

        elif "genmove" in command:
            # move = make_random_move(WHITE) if command.split()[-1] == 'W' else make_random_move(BLACK)
            # move = make_random_move(WHITE if command.split()[-1] == "W" else BLACK)
            print("=",genmove(WHITE if command.split()[-1] == "W" else BLACK)+"\n")
        
        elif "score" in command:
            val = score()
            print(f"={val}\n")
        elif "quit" in command:
            sys.exit()
        elif "mode" in command:
            MODE = command.split()[-1]
            if MODE not in ["e", "m", "h"]:
                eprint("? mode not supported. select e, m, or h\n")
        else:
            print("=?\n")  # skip currently unsupported commands


# start GTP communication
gtp()

# set_board_size('boardsize 9')
# print(get_board_index('J1')) #108
# print(get_board_index('D0')) # 12
# print(get_position_from_index(208))
# print(f'len {len(board)}')
# print(make_random_move(WHITE))
# print_board()
# captures(BLACK)
# print_board()
# print_board_num()
