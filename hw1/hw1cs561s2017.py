"""
AI Homework #1: Adversarial Search - Reversi
Author: Wei-Chi Chen (Vic)
"""
import copy
D_F = False  # Debug_Flag
INPUT_FILE = "input.txt"
OUTPUT_FILE = "output.txt"

# Initialize Variables
alpha = -1 * float("inf")
beta = float("inf")


# start define class
class GameState:
    WEIGHTED_FUNCTION = [
        [99, -8, 8, 6, 6, 8, -8, 99],
        [-8, -24, -4, -3, -3, -4, -24, -8],
        [8, -4, 7, 4, 4, 7, -4, 8],
        [6, -3, 4, 0, 0, 4, -3, 6],
        [6, -3, 4, 0, 0, 4, -3, 6],
        [8, -4, 7, 4, 4, 7, -4, 8],
        [-8, -24, -4, -3, -3, -4, -24, -8],
        [99, -8, 8, 6, 6, 8, -8, 99],
    ]
    player = "*"  # read file then constant
    x_player = 0  # read file then constant
    o_player = 0  # read file then constant
    depth = 0  # read file then constant
    now_depth = 0
    node = "root"
    best_node = "root"
    value = (-1 * float("inf"))
    alpha = (-1 * float("inf"))
    beta = float("inf")
    input_state = []  # read file then constant
    now_state = []
    prev_state = []
    best_state = []
    log_track = []
    x_pass = False
    o_pass = False

    def __init__(self):  # Constructor
        # self.state = init_game_num()
        self.init_game()

    def init_game(self):
        input_file = open(INPUT_FILE, "r")
        tmp = input_file.readline()
        if tmp[0] == "X":
            self.x_player = 1
            self.o_player = -1
            self.player = "X"
            x_num = 1
            o_num = -1
        else:
            self.x_player = -1
            self.o_player = 1
            self.player = "O"
            x_num = -1
            o_num = 1
        self.depth = int(input_file.readline())

        for i in range(8):
            row = []
            tmp = input_file.readline()
            for j in range(8):
                if tmp[j] == "X":
                    row.append(x_num)
                elif tmp[j] == "O":
                    row.append(o_num)
                else:  # tmp[j] == "*"
                    row.append(0)
            self.input_state.append(row)
        self.now_state = copy.deepcopy(self.input_state)
        self.prev_state = copy.deepcopy(self.input_state)
        self.best_state = copy.deepcopy(self.input_state)
        input_file.close()
        return

    def dump_state(self):
        if D_F:
            print "player:%s, depth:%s/%s, value:%s" % (self.player, self.now_depth, self.depth, self.value)
            self.show_board(self.now_state)

    def show_board(self, board_state):
        """
        Trans num_board to show xo_board on console
        :param board_state: just board state
        :return:
        """
        player = "*"
        oppo = "*"
        if self.player == "X":
            player = "X"
            oppo = "O"
        else:
            player = "O"
            oppo = "X"
        for item in board_state:
            print_row = ""
            for i in item:
                if i == 1:
                    print_row += player
                elif i == -1:
                    print_row += oppo
                else:
                    print_row += "*"
            if D_F: print print_row
        return

    def output_result(self):
        # output board
        output_file = open(OUTPUT_FILE, "w")
        x_num = self.x_player
        y_num = self.o_player
        for i in range(8):
            tmp = ""
            for j in range(8):
                if self.best_state[i][j] == x_num:
                    tmp += "X"
                elif self.best_state[i][j] == y_num:
                    tmp += "O"
                else:
                    tmp += "*"
            output_file.write(tmp + "\n")

        # output log
        output_file.write("Node,Depth,Value,Alpha,Beta\n")
        for item in self.log_track:
            for i in range(5):
                tmp = str(item[i])
                if tmp == "inf":
                    tmp = "Infinity"
                elif tmp == "-inf":
                    tmp = "-Infinity"

                if i != 4:
                    tmp += ","

                output_file.write(tmp)

            output_file.write("\n")

        output_file.close()
        return

# end define class


# start define functions


def show_board(board_state):
    """
    Trans num_board to show xo_board on console
    :param board_state:
    :return:
    """
    player = "*"
    oppo = "*"
    if board_state['player'] == "X":
        player = "X"
        oppo = "O"
    else:
        player = "O"
        oppo = "X"

    for item in board_state['now_state']:
        print_row = ""
        for i in item:
            if i == 1:
                print_row += player
            elif i == -1:
                print_row += oppo
            else:
                print_row += "*"
        if D_F: print print_row
    return


def output_result(now_state):
    # output board
    output_file = open("output.txt", "w")
    x_num = now_state['x_player']
    y_num = now_state['o_player']
    for i in range(8):
        tmp = ""
        for j in range(8):
            if now_state['now_state'][i][j] == x_num:
                tmp += "X"
            elif now_state['now_state'][i][j] == y_num:
                tmp += "O"
            else:
                tmp += "*"
        output_file.write(tmp + "\n")

    # output log
    output_file.write("Node,Depth,Value,Alpha,Beta" + "\n")

    output_file.close()
    return now_state


def EVAL(board_state):
    # wf: weighted function
    value = 0
    for i in range(8):
        for j in range(8):
            if board_state[i][j] != 0:
                value += board_state[i][j] * gs.WEIGHTED_FUNCTION[i][j]
    return value


def cut_off_test(gs, depth):
    # TODO: Not sue if need to check terminal game state here.
    if depth >= gs.depth:
        return True
    else:
        return False


def terminal_test(gs, depth):
    if gs.x_pass and gs.o_pass:
        if D_F: print "both pass"
        return True
    else:
        return False


def return_turn_player_number(gs, depth):
    num = 0
    if depth % 2 == 0:  # modified 1 -> 0
        # player's turn
        num = 1
    else:
        # opponent's turn
        num = -1
    return num


def find_move(gs, depth):
    """
    Find next move, and stored in move_queue[]
    each move format is [y, x]
    :param gs: GameState object
    :return:
    """
    # find next move
    now_mover = return_turn_player_number(gs, depth)
    now_oppo = -1 * now_mover
    move_queue = []
    board = gs.now_state[:]

    # can we check valid move and flip the board at the same time?
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                valid = False
                if j + 1 < 8 and board[i][j + 1] == now_oppo:  # right dir
                    for k in range(j + 2, 8, 1):
                        if board[i][k] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[i][k] == 0:  # There are not self disc
                            break
                if (not valid) and j - 1 >= 0 and board[i][j - 1] == now_oppo:  # left dir
                    for k in range(j - 2, -1, -1):
                        if board[i][k] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[i][k] == 0:  # There are not self disc
                            break
                if (not valid) and i - 1 >= 0 and board[i - 1][j] == now_oppo:  # up dir
                    for k in range(i - 2, -1, -1):
                        if board[k][j] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[k][j] == 0:  # There are not self disc
                            break
                if (not valid) and i + 1 < 8 and board[i + 1][j] == now_oppo:  # down dir
                    for k in range(i + 2, 8, 1):
                        if board[k][j] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[k][j] == 0:  # There are not self disc
                            break
                if (not valid) and i - 1 >= 0 and j - 1 >= 0 and board[i - 1][j - 1] == now_oppo:  # left-up
                    ii = i - 2
                    jj = j - 2
                    while ii >= 0 and jj >= 0:
                        if board[ii][jj] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[ii][jj] == 0:  # There are not self disc
                            break
                        ii -= 1
                        jj -= 1
                if (not valid) and i - 1 >= 0 and j + 1 < 8 and board[i - 1][j + 1] == now_oppo:  # right-up
                    ii = i - 2
                    jj = j + 2
                    while ii >= 0 and jj < 8:
                        if board[ii][jj] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[ii][jj] == 0:  # There are not self disc
                            break
                        ii -= 1
                        jj += 1
                if (not valid) and i + 1 < 8 and j - 1 >= 0 and board[i + 1][j - 1] == now_oppo:  # left-down
                    ii = i + 2
                    jj = j - 2
                    while ii < 8 and jj >= 0:
                        if board[ii][jj] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[ii][jj] == 0:  # There are not self disc
                            break
                        ii += 1
                        jj -= 1
                if (not valid) and i + 1 < 8 and j + 1 < 8 and board[i + 1][j + 1] == now_oppo:  # right-down
                    ii = i + 2
                    jj = j + 2
                    while ii < 8 and jj < 8:
                        if board[ii][jj] == now_mover:
                            move_queue.append([i, j])
                            valid = True
                            break
                        elif board[ii][jj] == 0:  # There are not self disc
                            break
                        ii += 1
                        jj += 1
    if D_F: print "find next move:", move_queue
    return move_queue


def execute_move(gs, depth, move):
    # show_board(state)
    if move == "pass":
        if D_F: print "pass, don't change any thing"
        return gs
    gs.prev_state = copy.deepcopy(gs.now_state)
    player = return_turn_player_number(gs, depth)
    oppo = -1 * player
    board = gs.now_state[:]
    my = move[0]  # move y
    mx = move[1]  # move x
    node = trans_move_to_node(move)
    if D_F: print "player:%s, move:%s(%s)" % (player, move, node)
    board[my][mx] = player  # execute mov
    # flip board
    if mx + 1 < 8 and board[my][mx + 1] == oppo:
        flip = False
        mark = 0
        for k in range(mx + 2, 8, 1):
            if board[my][k] == player:
                flip = True
                mark = k
                break
            elif board[my][k] == 0:
                break
        if flip:
            for k in range(mx + 1, mark, 1):
                board[my][k] = player
    if mx - 1 >= 0 and board[my][mx - 1] == oppo:
        flip = False
        mark = 0
        for k in range(mx - 2, -1, -1):
            if board[my][k] == player:
                flip = True
                mark = k
                break
            elif board[my][k] == 0:
                break
        if flip:
            for k in range(mx - 1, mark, -1):
                board[my][k] = player
    if my + 1 < 8 and board[my + 1][mx] == oppo:
        flip = False
        mark = 0
        for k in range(my + 2, 8, 1):
            if board[k][mx] == player:
                flip = True
                mark = k
                break
            elif board[k][mx] == 0:
                break
        if flip:
            for k in range(my + 1, mark, 1):
                board[k][mx] = player
    if my - 1 >= 0 and board[my - 1][mx] == oppo:
        flip = False
        mark = 0
        for k in range(my - 2, -1, -1):
            if board[k][mx] == player:
                flip = True
                mark = k
                break
            elif board[k][mx] == 0:
                break
        if flip:
            for k in range(my - 1, mark, -1):
                board[k][mx] = player
    if my - 1 >= 0 and mx - 1 >= 0 and board[my - 1][mx - 1] == oppo:
        flip = False
        mark_x = 0
        mark_y = 0
        ii = my - 2
        jj = mx - 2
        while ii >= 0 and jj >= 0:
            if board[ii][jj] == player:
                flip = True
                mark_y = ii
                mark_x = jj
                break
            elif board[ii][jj] == 0:
                break
            ii -= 1
            jj -= 1
        if flip:
            flip_x = mx
            flip_y = my
            while flip_y > mark_y and flip_x > mark_x:
                board[flip_y][flip_x] = player
                flip_y -= 1
                flip_x -= 1
    if my - 1 >= 0 and mx + 1 < 8 and board[my - 1][mx + 1] == oppo:
        flip = False
        mark_x = 0
        mark_y = 0
        ii = my - 2
        jj = mx + 2
        while ii >= 0 and jj < 8:
            if board[ii][jj] == player:
                flip = True
                mark_y = ii
                mark_x = jj
                break
            elif board[ii][jj] == 0:
                break
            ii -= 1
            jj += 1
        if flip:
            flip_x = mx
            flip_y = my
            while flip_y > mark_y and flip_x < mark_x:
                board[flip_y][flip_x] = player
                flip_y -= 1
                flip_x += 1
    if my + 1 < 8 and mx - 1 >= 0 and board[my + 1][mx - 1] == oppo:
        flip = False
        mark_x = 0
        mark_y = 0
        ii = my + 2
        jj = mx - 2
        while ii < 8 and jj >= 0:
            if board[ii][jj] == player:
                flip = True
                mark_y = ii
                mark_x = jj
                break
            elif board[ii][jj] == 0:
                break
            ii += 1
            jj -= 1
        if flip:
            flip_x = mx
            flip_y = my
            while flip_y < mark_y and flip_x > mark_x:
                board[flip_y][flip_x] = player
                flip_y += 1
                flip_x -= 1
    if my + 1 < 8 and mx + 1 < 8 and board[my + 1][mx + 1] == oppo:
        flip = False
        mark_x = 0
        mark_y = 0
        ii = my + 2
        jj = mx + 2
        while ii < 8 and jj < 8:
            if board[ii][jj] == player:
                flip = True
                mark_y = ii
                mark_x = jj
                break
            elif board[ii][jj] == 0:
                break
            ii += 1
            jj += 1
        if flip:
            flip_x = mx
            flip_y = my
            while flip_y < mark_y and flip_x < mark_x:
                board[flip_y][flip_x] = player
                flip_y += 1
                flip_x += 1

    # Move state to last state
    gs.now_state = copy.deepcopy(board)
    gs.value = EVAL(gs.now_state)  # count now board value

    # if D_F: print "After move:", move
    # gs.dump_state()
    # show_board(state)

    return gs


def copy_board_state(from_state):
    # input 2-d list
    board_state = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

    for i in range(8):
        for j in range(8):
            board_state[i][j] = int(from_state[i][j])
    return board_state


def trans_move_to_node(move):
    if move == "pass":
        return "pass"
    elif move == "root":
        return "root"
    else:
        trans_table = ["a", "b", "c", "d", "e", "f", "g", "h"]
        node = trans_table[move[1]]
        node += str(move[0]+1)
        return node


def trans_node_to_move(node):
    trans_table = ["a", "b", "c", "d", "e", "f", "g", "h"]
    my = trans_table.index(node[1])
    mx = int(node[0]) - 1
    move = [my, mx]
    return move


def set_pass_flag(depth, if_pass):
    if depth % 2 == 1:  # no matter modulize, if they are different will be ok
        gs.x_pass = if_pass
    else:
        gs.o_pass = if_pass
    return


def dump_node(gs):
    if D_F: print "node:%s,depth:%s,value:%s,a:%s,b:%s" % (gs.node, gs.now_depth, gs.value, gs.alpha, gs.beta)
    return


def calculate_alg(gs):
    dump_node(gs)  # start
    if gs.depth > 0:
        max_value(gs, gs.now_state, gs.now_depth, gs.value, alpha, beta)
    return


def update_state_and_log(gs, node, depth, value, alpha, beta):
    log = [node, depth, value, alpha, beta]
    if D_F: print log
    gs.log_track.append(log)
    # gs.now_depth -= 1
    return


def max_value(gs, state, depth, value, alpha, beta):
    """
    Fisrt in is Node: root, we can imagine that initial state is player think about the "move",
    we want to pick up the best move(highest heuristic function) we could get.
    Then, update the alpha at max_value level

    2/6 try to revise Alg. to feat test case 4

    :param gs:
    :param state:
    :param depth:
    :param value:
    :param alpha:
    :param beta:
    :return:
    """
    # choose the max value move, first time call is root
    node = gs.node  # node information is brought by gs object
    this_node_state = copy.deepcopy(state)  # Speically copy for the list "instance"

    if D_F: print "into max_value(node %s)" % node

    # Cut-Off test and Terminal test
    if cut_off_test(gs, depth) or terminal_test(gs, depth):
        if D_F: print "cut off! This leaf:", node
        eval_value = EVAL(this_node_state)  # node value
        gs.value = eval_value

        # Log the leaf value ?
        update_state_and_log(gs, node, depth, eval_value, alpha, beta)
        # gs.now_depth = depth - 1
        return eval_value

    # Incoming node log
    # if depth == 0:
    value = -1 * float("inf")
    update_state_and_log(gs, node, depth, value, alpha, beta)

    # find next move
    # depth += 1
    move_queue = find_move(gs, depth)
    if len(move_queue) == 0:
        # pass move
        set_pass_flag(depth, True)  # set pass
        if D_F: print "player will pass this turn:", depth
        move_queue = ["pass"]
    else:
        set_pass_flag(depth, False)  # clear pass flag

    # expend successors
    for step in move_queue:  # pick out best!
        # Real move, need to update the now node
        execute_move(gs, depth, step)  # gs.now_state has been changed
        gs.node = trans_move_to_node(step)
        tmp_state = copy.deepcopy(gs.now_state)
        # alpha = max(alpha, min_value(gs))
        if D_F: print "befor max find value:", value
        value = max(value, min_value(gs, tmp_state, depth+1, value, alpha, beta))

        # pruning out
        if value >= beta:
            # gs.value = eval_value
            update_state_and_log(gs, node, depth, value, alpha, beta)
            if D_F: print "pruning by alpha >= beta"
            return value  # beta

        # checking update alpha
        if value > alpha:
            alpha = value
            if depth == 0:  # because only next move will be do
                gs.best_state = copy.deepcopy(tmp_state)
                gs.best_node = trans_move_to_node(step)
            gs.alpha = alpha
            if D_F: print "update alpha", alpha
        update_state_and_log(gs, node, depth, value, alpha, beta)
        # else:
        #    update_state_and_log(gs, node, depth, alpha, alpha, beta)
        # let for loop have the same state to calculate
        # update_state_and_log(gs, node, depth - 1, eval_value, alpha, beta)
        # update_state_and_log(gs, node, depth-1, value, alpha, beta)
        # recover state for this for loop
        gs.now_state = copy.deepcopy(this_node_state)

    # root exiting log
    # if depth == 0:
    #    update_state_and_log(gs, node, depth, value, alpha, beta)

    return value  # value


def min_value(gs, state, depth, value, alpha, beta):

    # choose the min value move, first time call is root's next move
    node = gs.node  # node information is brought by gs object
    this_node_state = copy.deepcopy(state)  # Speically copy for the list "instance"

    if D_F: print "into min_value(node %s)" % node

    # Cut-Off test and Terminal test
    if cut_off_test(gs, depth) or terminal_test(gs, depth):
        if D_F: print "cut off! This leaf:", node
        eval_value = EVAL(this_node_state)  # node value
        gs.value = eval_value

        # Log the leaf value ?
        update_state_and_log(gs, node, depth, eval_value, alpha, beta)
        # gs.now_depth = depth - 1
        return eval_value

    # Incoming node log
    # if depth == 0:
    value = float("inf")
    update_state_and_log(gs, node, depth, value, alpha, beta)

    # find next move
    # depth += 1
    move_queue = find_move(gs, depth)
    if len(move_queue) == 0:
        # pass move
        set_pass_flag(depth, True)  # set pass
        if D_F: print "player will pass this turn:", depth
        move_queue = ["pass"]
    else:
        set_pass_flag(depth, False)  # clear pass flag

    # expend successors
    for step in move_queue:
        # print "before execute:", step
        # gs.dump_state()
        # Real move, need to update the now node
        execute_move(gs, depth, step)  # gs.now_state has been changed
        gs.node = trans_move_to_node(step)
        tmp_state = copy.deepcopy(gs.now_state)
        # beta = min(beta, max_value(gs))
        # if step == "pass":
        #    value = min(value, max_value(gs, tmp_state, depth + 1, value, alpha, beta))
        if D_F: print "befor min find value:", value
        value = min(value, max_value(gs, tmp_state, depth+1, value, alpha, beta))

        # Pruning out
        if value <= alpha:
            # gs.value = eval_value
            update_state_and_log(gs, node, depth, value, alpha, beta)
            if D_F: print "pruning by beta < alpha"
            return value  # alpha

        if value < beta:
            beta = value
            # gs.best_state = copy.deepcopy(gs.now_state)
            # gs.best_node = trans_move_to_node(step)
            gs.beta = beta
            if D_F: print "update beta:", beta
        update_state_and_log(gs, node, depth, value, alpha, beta)
        # else:
        #    update_state_and_log(gs, node, depth, beta, alpha, beta)

        # let for loop have the same state to calculate
        # update_state_and_log(gs, node, depth - 1, eval_value, alpha, beta)
        # update_state_and_log(gs, node, depth - 1, value, alpha, beta)
        # recover state for this for loop
        gs.now_state = copy.deepcopy(this_node_state)

    # update_state_and_log(gs, node, depth, eval_value, alpha, beta)
    return value  # beta is old version


# end define functions

# main flow started
gs = GameState()

# test
# move = find_move(gs)
# state = execute_move(gs, move[0])
calculate_alg(gs)

# max_value(gs)
if D_F:
    print "Result:", gs.best_node
    gs.show_board(gs.best_state)
gs.output_result()
