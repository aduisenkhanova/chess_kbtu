import pygame as p
from pygame import mixer

p.init()

p.display.set_caption('Chess')
icon = p.image.load('icon.png')
p.display.set_icon(icon)

WIDTH = HEIGHT = 520
DIMENSION = 8

SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

FONT_BOLD = 'fonts/OpenSans-SemiBold.ttf'
FONT_REG = 'fonts/OpenSans-Regular.ttf'
FONT_LIGHT = 'fonts/OpenSans-Light.ttf'

screen = p.display.set_mode((WIDTH, HEIGHT))

need_input1 = False
need_input2 = False
player1 = ''
player2 = ''


class GameState:

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False

    '''takes a Move as a parameter and executes it'''
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)  # log the move so we can undo it later
        self.white_to_move = not self.white_to_move  # swap player
        # update the king's location if moved
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            # update the king's position if needed
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

    '''
    All moves considering checks
    '''
    def get_valid_moves(self):
        # 1) generate all possible moves
        moves = self.get_all_possible_moves()
        # 2) for each move, make a move
        for i in range(len(moves)-1, -1, -1):  # when removing from a list got backwards through that list
            self.make_move(moves[i])
            # 3) generate all opponent's moves
            # 4) for each of your opponent's moves, see if they attack your king
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])  # 5) if they do attack your king, not a valid move
            self.white_to_move = not self.white_to_move
            self.undo_move()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.check_mate:
                self.check_mate = True
            else:
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False
        return moves

    '''
    Determine if the current player in check
    '''
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    '''
    Determine if the enemy can attack the square r, c
    '''
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move  # switch to opponent's turn
        opp_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # switch turns back
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:  # square is under attack
                return True
        return False

    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)  # calls the appropriate move function
        return moves

    '''
    Get all pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:  # white pawn moves
            if self.board[r-1][c] == "--":  # 1 square advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square moves
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c-1 >= 0:  # captures to the left
                if self.board[r - 1][c - 1][0] == "b":  # enemy piece t capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c+1 <= 7:  # captures to the right
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece t capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:  # black pawn moves
            if self.board[r+1][c] == "--":  # 1 square advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square moves
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c-1 >= 0:  # captures to the left
                if self.board[r + 1][c - 1][0] == "w":  # enemy piece t capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c+1 <= 7:  # captures to the right
                if self.board[r + 1][c + 1][0] == "w":  # enemy piece t capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    '''
    Get all rook moves for the rook located at row, col and add these moves to the list
    '''
    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # empty piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else: # friendly piece
                        break
                else:  # off board
                    break

    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2))
        ally_color = "w" if self.white_to_move else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        enemy_color = "b" if self.white_to_move else "w"
        for d in directions:
            for i in range(1, 8):  # bishop can move max in 7 squares
                end_row = r + d[0] * i
                end_col = c + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # empty piece valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        king_moves = ((-1, -1), (1, -1), (-1, 1), (1, 1), (-1, -0), (1, 0), (0, -1), (0, 1))
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))


class Move:

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_rank = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]  # starting point
        self.piece_captured = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        # print(self.moveID)
    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        return self.get_rank_files(self.start_row, self.start_col) + self.get_rank_files(self.end_row, self.end_col)

    def get_rank_files(self, r, c):
        return self.cols_to_files[c] + self.rows_to_rank[r]


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


'''Highlight square selected and moves for piece selected'''


def highlight_squares(sc, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))  # highlight selected square
            s.set_alpha(100)  # transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('yellow'))
            sc.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            s.fill(p.Color('green'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    sc.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))


def draw_game_state(sc, gs, valid_moves, sq_selected):
    draw_board(sc)
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(sc, gs.board)


def draw_board(sc):
    colors = [p.Color(242, 238, 220), p.Color(87, 58, 46)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            p.draw.rect(sc, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(sc, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                sc.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_text(text, s, x, y):
    font = p.font.SysFont(FONT_BOLD, s, True, False)
    text_object = font.render(text, False, p.Color('Gray'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(x, y)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))


def get_input():

    global need_input1, need_input2, player1, player2
    input_player1 = p.Rect(120, 300, 110, 30)
    input_player2 = p.Rect(320, 300, 110, 30)

    p.draw.rect(screen, (255, 255, 255), input_player1)
    p.draw.rect(screen, (255, 255, 255), input_player2)

    mouse = p.mouse.get_pos()
    click = p.mouse.get_pressed()

    if input_player1.collidepoint(mouse[0], mouse[1]) and click[0]:
        need_input1 = True

    if need_input1:
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.type == p.K_RETURN:
                    need_input1 = False
                    player1 = ''
                elif e.type == p.K_BACKSPACE:
                    player1 = player1[:-1]
                else:
                    player1 += e.unicode

    if input_player2.collidepoint(mouse[0], mouse[1]) and click[0]:
        need_input2 = True

    if need_input2:
        for e in p.event.get():
            if e.type == p.KEYDOWN:
                if e.type == p.K_RETURN:
                    need_input2 = False
                    player2 = ''
                elif e.type == p.K_BACKSPACE:
                    player2 = player2[:-1]
                else:
                    player2 += e.unicode

    draw_text("White", 30, 50, 305)
    draw_text(player1, 30, 120, 305)
    draw_text("Black", 30, 250, 305)
    draw_text(player2, 30, 320, 305)


def text_objects(text, font):
    text_surface = font.render(text, True, p.Color(0, 0, 0))
    return text_surface, text_surface.get_rect()


def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = p.mouse.get_pos()
    click = p.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        p.draw.rect(screen, ac, (x, y, w, h))

        if click[0] == 1 and action is not None:
            action()
    else:
        p.draw.rect(screen, ic, (x, y, w, h))

    text_surf, text_rect = text_objects(msg, MEDIUM_TEXT)
    text_rect.center = ((x+(w/2)), (y+(h/2)))
    screen.blit(text_surf, text_rect)


def quit_game():
    p.quit()


def unpause():
    mixer.music.play()


def pause():
    mixer.music.pause()


def pause_game():
    clock = p.time.Clock()
    paused = True
    while paused:
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()

        draw_text('Paused. Press enter to continue', 40, 15, 255)
        keys = p.key.get_pressed()
        if keys[p.K_RETURN]:
            paused = False
        p.display.update()
        clock.tick(MAX_FPS)


def main():
    clock = p.time.Clock()
    screen.fill(p.Color("grey"))
    gs = GameState()

    valid_moves = gs.get_valid_moves()
    move_made = False  # flag variable for when a move is made
    load_images()
    run = True
    sq_selected = ()  # no square selected initially. but this simply keep track of the last click of the user
    player_clicks = []  # keep track of user clicks
    game_over = False
    while run:
        for e in p.event.get():
            if e.type == p.QUIT:
                run = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x,y) location of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sq_selected == (row, col):  # the user clicked the same coordinate/square twice
                        sq_selected = ()  # deselect
                        player_clicks = []  # clear player clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)  # append for 1st and 2nd clicks
                    if len(player_clicks) == 2:  # after the 2nd click
                        move = Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                sq_selected = ()  # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                if e.key == p.K_r:
                    gs = GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                if e.key == p.K_ESCAPE:
                    pause_game()

        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
            mixer.music.load("move.wav")
            mixer.music.play()

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.check_mate:
            game_over = True
            if gs.white_to_move:
                draw_text('BLACK WINS!', 70, 150, 230)
            else:
                draw_text('WHITE WINS!', 70, 150, 230)
        elif gs.stale_mate:
            game_over = True
            draw_text('Stalemate', 70, 120, 230)

        p.display.update()
        clock.tick(MAX_FPS)

    p.quit()


def game_intro():
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    mixer.music.load("classical.wav")
    mixer.music.play(-1)

    bg = p.image.load("bg.png")
    run = True

    while run:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                quit()

        screen.blit(p.transform.scale(bg, (WIDTH, HEIGHT)), (0, 0))

        text_surf, text_rect = text_objects('C H E S S', MENU_TEXT)
        text_rect.center = (int(WIDTH / 2), int(HEIGHT * 0.35))
        screen.blit(text_surf, text_rect)
        text_surf, text_rect = text_objects('Created by Aizada, Akbota, Assel, Malika', MEDIUM_TEXT)
        text_rect.center = (int(WIDTH / 2), int(HEIGHT * 0.9))
        screen.blit(text_surf, text_rect)
        acolor = p.Color(185, 116, 85)
        icolor = p.Color(237, 184, 121)
        button("Start", 70, 400, 80, 30, acolor, icolor, main)
        button("Quit", 170, 400, 80, 30, acolor, icolor, quit_game)
        button("Sound On", 270, 400, 80, 30, acolor, icolor, unpause)
        button("Sound Off", 370, 400, 80, 30, acolor, icolor, pause)

        get_input()

        p.display.update()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    p.init()
    MENU_TEXT = p.font.Font(FONT_REG, int(150 / 1080 * HEIGHT))
    LARGE_TEXT = p.font.Font(FONT_LIGHT, int(60 / 1080 * HEIGHT))
    MEDIUM_TEXT = p.font.Font(FONT_LIGHT, int(40 / 1440 * HEIGHT))
    SMALL_TEXT = p.font.Font(FONT_BOLD, int(25 / 1440 * HEIGHT))

    game_intro()
