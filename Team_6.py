
import STcpClient
import copy

'''
    輪到此程式移動棋子
    board : 棋盤狀態(list of list), board[i][j] = i row, j column 棋盤狀態(i, j 從 0 開始)
            0 = 空、1 = 黑、2 = 白
    is_black : True 表示本程式是黑子、False 表示為白子

    return step
    step : list of list, step = [(r1, c1), (r2, c2) ...]
            r1, c1 表示要移動的棋子座標 (row, column) (zero-base)
            ri, ci (i>1) 表示該棋子移動路徑
'''
Empty_block = 0
Black_piece = 1
White_piece = 2
Trace_block = 3

debug = False
info = lambda x :print(x) if debug else None

def judge_ally_present(is_black):
    if is_black:
        ally_piece = Black_piece
        enem_piece = White_piece
    else:
        ally_piece = White_piece
        enem_piece = Black_piece
    return ally_piece, enem_piece

class Board:
    def __init__(self,raw_board,is_black):
        self.raw_board:list[list[int]] = raw_board
        self.ally_piece:list[tuple[int,int]] = []
        self.enem_piece:list[tuple[int,int]] = []
        ally_piece, enem_piece = judge_ally_present(is_black)

        self.control:int = ally_piece
        self.against:int = enem_piece

        for y in range(len(raw_board)):
            for x in range(len(raw_board[y])):
                cur_piece = raw_board[y][x]
                if cur_piece == ally_piece:
                    self.ally_piece.append((y, x))
                if cur_piece == enem_piece:
                    self.enem_piece.append((y, x))

    def get_move(self,of_ally=True):
        board = self.raw_board
        boards_did_move = []
        if of_ally:
            pieces = self.ally_piece
        else:
            pieces = self.enem_piece

        for piece in pieces:
            board_will_move = Simplified_board(board, piece)
            info("board_will_move")
            boards_did_move.append(board_will_move)
            y, x = piece
            cases = []
            # y軸
            if piece:
                if y > 1:
                    cases.append(('y-', board[y - 1][x], board[y - 2][x]))
                elif y == 1:
                    cases.append(('y-', board[y - 1][x], None))
                if y < 6:
                    cases.append(('y+', board[y + 1][x], board[y + 2][x]))
                elif y == 6:
                    cases.append(('y+', board[y + 1][x], None))

                # X軸
                if x > 1:
                    cases.append(('x-',board[y][x - 1], board[y][x - 2]))
                elif x == 1:
                    cases.append(('x-',board[y][x - 1], None))
                if x < 6:
                    cases.append(('x+',board[y][x + 1], board[y][x + 2]))
                elif x == 6:
                    cases.append(('x+',board[y][x + 1], None))

            for test_case in cases:
                if test_case[1] == Empty_block: # 離邊界至少一格遠 這方向沒有被擋住，可以走到這格並結束
                    board_will_move.make_move(test_case[0],1)
                    pass

                if (test_case[1] == self.control and test_case[2] == Empty_block) or \
                    (test_case[1] == self.against and test_case[2] in [Empty_block,Trace_block]): # 可以跳過棋子
                    board_will_move.make_move(test_case[0],2)
                    pass
            info(board_will_move.moves.items())
            return board_will_move

def direction_to_change(direction, step, y, x):
    if direction == 'y+':
        y += step
    if direction == 'y-':
        y -= step
    if direction == 'x+':
        x += step
    if direction == 'x-':
        x -= step
    return y, x

class Simplified_board:
    def __init__(self,raw_board:list,focus:tuple,trace:list = []):
        self.raw_board:list[list[int]] = raw_board
        ally_piece, enem_piece = judge_ally_present(is_black)

        y, x = focus
        self.control:int = self.raw_board[y][x]
        self.trace:list = copy.deepcopy(trace)
        self.trace.append(focus)
        self.focus:tuple[int, int] = focus
        self.moves:dict[tuple[tuple[int,int]]:Simplified_board] = {}
        self.evaluation:dict = dict(under_danger_piece=-1,ate_piece=-1,reach_goal_piece=-1)

    def make_move(self,direction:str,step:int):
        focus = copy.deepcopy(self.focus)
        y, x = focus
        board_did_move = copy.deepcopy(self.raw_board)
        board_did_move[y][x] = 3

        y,x = direction_to_change(direction,step,y,x)
        board_did_move[y][x] = self.control
        info((y, x, self.control, direction,step))
        new_trace = copy.deepcopy(self.trace)

        info(new_trace)
        info("Did new board")
        self.moves[tuple(new_trace)] = Simplified_board(board_did_move, (y, x), new_trace)
        info(new_trace)

    # TODO: complete evaluation function
    def evaluate(self):
        pass

def GetStep(board, is_black):
    board_this_step = Board(board, is_black)
    board = board_this_step.get_move(True)
    for trace, b in board.moves.items():
        print(b.trace)
        return b.trace
    # fill your program here
    pass


if debug:
    board = [[0 for i in range(8)] for i in range(8)]
    board[3][3] = 1
    is_black = True
    list = GetStep(board, is_black)
    print(list)

    list = GetStep(board, is_black)
    print(list)
    exit(0)


while(True):
    (stop_program, id_package, board, is_black) = STcpClient.GetBoard()
    if(stop_program):
        break
    
    listStep = GetStep(board, is_black)
    STcpClient.SendStep(id_package, listStep)
