import random

n = k = 0
moves = []

def initialize(num, sel):
    global n, k, moves
    n = num
    k = sel
    moves = []
    guess = []
    for _ in range(k):
        guess.append(random.randint(0,n-1))

    moves.append(guess)

def get_second_player_move():
    global n, k, moves

    return moves[len(moves)-1]

def put_first_player_response(red, white):
    global n, k, moves

    pass

def printit():
    global n, k
    print(n, k)