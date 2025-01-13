
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
    print(*args, file=sys.stderr, **kwargs)


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
    return size


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
        if piece == OFFBOARD:
            continue
        # same color
        if piece & color:
            # count liberties
            count_liberties(square, color)
            # if no liberties then remove the stones
            if len(liberties) == 0:
                clear_block()
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


def set_move(square, color):
    board[square] = color
    # handle capture of opposite color
    captures(3 - color)


def remove_move(square):
    board[square] = EMPTY


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

    # count liberties
    count_liberties(square, color)
    # check for suicide move
    if len(liberties) == 0:
        restore_board()
        # take off the stone
        board[square] = EMPTY
        # search another move
        try:
            return make_random_move(color)
        except:
            return ""

    restore_board()
    print(f"random move {get_position_from_index(square)}")
    return get_position_from_index(square)


def make_random_move_without_set(color):
    square = random.randrange(BOARD_RANGE, len(board) - BOARD_RANGE - 1)
    while board[square] != 0:
        square = random.randrange(BOARD_RANGE, len(board) - BOARD_RANGE - 1)

    if BOARD_RANGE < square < len(board) - BOARD_RANGE:
        square = square
    else:
        make_random_move(color)

    # count liberties
    count_liberties(square, color)
    # check for suicide move
    if len(liberties) == 0:
        restore_board()
        # take off the stone
        board[square] = EMPTY
        # search another move
        try:
            return make_random_move(color)
        except:
            return ""

    restore_board()
    print(f"random move {get_position_from_index(square)}")
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
        count_liberties(liberty, color)
        if len(liberties) > best_count and not detect_edge(liberty):
            best_count = len(liberties)
            best_liberty = liberty

        restore_board()
        board[liberty] = EMPTY

    return best_liberty


def genmove2(color):
    best_move = 0
    capture = 0
    save = 0
    defend = 0
    surround = 0

    # capture opponent's group
    for square in range(len(board)):
        piece = board[square]

        if piece & (3 - color):
            count_liberties(square, (3 - color))
            # if only 1 liberty left for opponent
            if len(liberties) == 1:
                target_square = liberties[0]
                best_move = target_square
                capture = target_square
                break
            restore_board()

    # save own group
    for square in range(len(board)):
        piece = board[square]

        if piece & color:
            count_liberties(square, color)
            # if only 1 liberty left for own
            if len(liberties) == 1:
                target_square = liberties[0]

                # checks edge points
                if not detect_edge(target_square):
                    best_move = target_square
                    save = target_square
                    break
            restore_board()

    # defend own group
    for square in range(len(board)):
        piece = board[square]

        if piece & color:
            count_liberties(square, color)
            # if 2 liberty left
            if len(liberties) == 2:
                best_liberty = evaluate_best_liberty(color)

                # checks edge points
                best_move = best_liberty
                defend = best_liberty
                break
            restore_board()

    # surround opponent's group
    for square in range(len(board)):
        piece = board[square]

        if piece & (3 - color):
            count_liberties(square, (3 - color))
            # if group 2 liberty left
            if len(liberties) > 1:
                best_liberty = evaluate_best_liberty(3 - color)

                # checks edge points
                best_move = best_liberty
                surround = best_liberty
                break

            restore_board()

    if best_move:
        eprint("save move", get_position_from_index(save))
        eprint("capture move", get_position_from_index(capture))
        eprint("defend move", get_position_from_index(defend))
        eprint("surround move", get_position_from_index(surround))

        random_action = random.randrange(2)

        # handle AI move priorities
        if not save and not capture and not defend:
            best_move = surround
        if not save and not capture and defend:
            best_move = defend if random_action else surround
        if not capture and save:
            best_move = save
        if capture:
            best_move = capture

        # make move
        set_move(best_move, color)
        # check validity if not suicide.
        count_liberties(best_move, color)
        legal = len(liberties)
        restore_board()
        if not legal:
            board[best_move] = EMPTY
            eprint("avoid suicide move")
            # make random move
            return make_random_move(color)

        eprint("best move", get_position_from_index(best_move))

        return get_position_from_index(best_move)

    return make_random_move(color)


def evaluate_fitness(move, color):
    # Initialize fitness components
    capture_score = 1
    save_score = 1
    defend_score = 1
    surround_score = 1
    
    # Get the board index for the move
    square = get_board_index(move)

    # Capture evaluation: Check if the move can capture opponent's stones
    count_liberties(square, 3 - color)
    if len(liberties) == 1:  
        capture_score = 10
    if len(liberties) > 2:  
        surround_score = 4  

    restore_board()

    # Save evaluation: Check if the move can save own stones from being captured
    count_liberties(square, color)
    if len(liberties) == 1: 
        save_score = 8  
    if len(liberties) == 2:  
        defend_score = 6
    restore_board()

    # Sum up the fitness scores with appropriate weights
    total_fitness = capture_score + save_score + defend_score + surround_score
    
    return total_fitness


def select_population(population, fitness_scores):
    total_fitness = sum(fitness_scores)
    selection_probs = [fitness / total_fitness for fitness in fitness_scores]

    selected_moves = random.choices(
        population, weights=selection_probs, k=len(population)
    )

    return selected_moves


def crossover_population(selected_moves):
    offspring = []

    for i in range(0, len(selected_moves), 2):
        parent1 = selected_moves[i]
        parent2 = selected_moves[i + 1 if i + 1 < len(selected_moves) else 0]

        # Simple one-point crossover
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]

        offspring.extend([child1, child2])

    return offspring


def mutate_population(offspring, mutation_rate, color):
    for i in range(len(offspring)):
        if random.random() < mutation_rate:
            # Perform mutation by generating a new random move
            offspring[i] = make_random_move_without_set(color)

    return offspring


def replace_population(population, offspring, fitness_scores, color):
    combined_population = population + offspring
    combined_fitness_scores = fitness_scores + [
        evaluate_fitness(move, color) for move in offspring
    ]

    # Sort combined population based on fitness scores
    sorted_population = [
        move
        for _, move in sorted(
            zip(combined_fitness_scores, combined_population), reverse=True
        )
    ]

    # Select the top individuals to form the new population
    return sorted_population[: len(population)]


def genmove(color):
    
    population_size = 50
    generations = 50
    mutation_rate = 0.1

    # initial population
    population = [make_random_move_without_set(color) for _ in range(population_size)]
    

    for generation in range(generations):
        fitness_scores = [evaluate_fitness(move, color) for move in population]
        # Selection
        selected_moves = select_population(population, fitness_scores)

        # Crossover
        offspring = crossover_population(selected_moves)

        # Mutation
        offspring = mutate_population(offspring, mutation_rate,color)

        # Evaluate fitness of new offspring
        fitness_scores = [evaluate_fitness(move, color) for move in offspring]

        # Replacement
        population = replace_population(population, offspring, fitness_scores, color)

    # Choose the best move 
    best_move = population[fitness_scores.index(max(fitness_scores))]

    set_move(get_board_index(best_move), color)
    # check validity if not suicide.
    count_liberties(get_board_index(best_move), color)
    legal = len(liberties)
    restore_board()
    if not legal:
        board[get_board_index(best_move)] = EMPTY
        eprint("avoid suicide move")
            # make random move
        return make_random_move(color)
    
    
    return best_move


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

            print("=", genmove(WHITE if command.split()[-1] == "W" else BLACK) + "\n")

        elif "score" in command:
            val = score()
            print(f"={val}\n")
        elif "quit" in command:
            sys.exit()
        else:
            print("=?\n")  # skip currently unsupported commands


# start GTP communication
gtp()
# set_board_size("boardsize 9")
# print(get_board_index('J1')) #108
# print(get_board_index('D0')) # 12
# print(get_position_from_index(208))
# print(f'len {len(board)}')
# print(make_random_move(WHITE))
# print_board()
# captures(BLACK)
# play("play W J2")
# print_board()
# # # print_board_num()
# b = genmove(BLACK)
# print(f"bestmove{b}")
# print_board()
