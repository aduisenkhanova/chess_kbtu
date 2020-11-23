import pygame as p
from pygame import mixer
from chess import ChessEngine


p.init()

p.display.set_caption('Chess')
icon = p.image.load('icon.png')
p.display.set_icon(icon)

WIDTH = HEIGHT = 400
DIMENSION = 8

SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

screen = p.display.set_mode((WIDTH, HEIGHT))

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def text_objects(text, font):
    textSurface = font.render(text, True, p.Color("black"))
    return textSurface, textSurface.get_rect()


def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = p.mouse.get_pos()
    click = p.mouse.get_pressed()

    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        p.draw.rect(screen, ac, (x, y, w, h))

        if click[0] == 1 and action is not None:
            action()
    else:
        p.draw.rect(screen, ic, (x, y, w, h))

    smallText = p.font.Font("freesansbold.ttf", 20)
    textSurf, textRect = text_objects(msg, smallText)
    textRect.center = ((x+(w/2)), (y+(h/2)))
    screen.blit(textSurf, textRect)


def gameIntro():
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

        screen.fill(p.Color(220, 211, 214))
        largeText = p.font.Font("freesansbold.ttf", 50)
        TextSurf, TextRect = text_objects("CHESS", largeText)
        TextRect.center = ((WIDTH / 2), (HEIGHT / 4))
        screen.blit(TextSurf, TextRect)

        button("Start", 50, 250, 100, 50, p.Color(87, 58, 46), p.Color(97, 58, 46), main)
        # button("Quit", 250, 250, 100, 50, p.Color(87, 58, 46), p.Color(97, 58, 46), p.quit)

        p.display.update()
        clock.tick(MAX_FPS)


def main():
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()

    validMoves = gs.getValidMoves()
    moveMade = False  # flag variable for when a move is made

    loadImages()
    running = True
    sqSelected = ()  # no square selected initially. but this simply keep track of the last click of the user
    playerClicks = []  # keep track of user clicks
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x,y) location of the mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row, col):  # the user clicked the same coordinate/square twice
                    sqSelected = ()  # deselect
                    playerClicks = []  # clear player clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)  # append for 1st and 2nd clicks
                if len(playerClicks) == 2:  # after the 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()  # reset user clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
            mixer.music.load("move.wav")
            mixer.music.play()

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    colors = [p.Color(220, 211, 214), p.Color(87, 58, 46)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    gameIntro()
