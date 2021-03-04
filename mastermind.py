import random
from z3 import *


# static variables for 1 game
n = k = 0
moves = []

# supplying new propositional variables
var_counter = 0
def count():
    global var_counter
    count = var_counter
    var_counter = var_counter +1
    return str(count)

def get_fresh_bool( suff = "" ):
    return Bool( "b_" + count() + "_" + suff )

def get_fresh_vec(length, suff = "" ):
    n_vs = []
    for _ in range(length):
        n_vs.append( get_fresh_bool( suff ) )
    return n_vs

#################### Helper functions ##########################
def at_most(vars, k):
    clauses = []
    if(k == 0):
        return [Not(pi) for pi in vars]
    if(k == len(vars)):
        return clauses

    s = [get_fresh_vec(k) for _ in range(len(vars))]

    # for p1
    clauses += [Or(Not(vars[0]),s[0][0])]
    clauses += [Not(s[0][i]) for i in range(1, k)]
    
    # for pi
    for i in range(1, len(vars)):
        clauses += [Or(Not(Or(vars[i], s[i-1][0])), s[i][0])]
        for j in range(1, k):
            clauses += [Or(Not(Or(And(vars[i], s[i-1][j-1]), s[i-1][j])), s[i][j])]
    
    # additional
    for i in range(1, len(vars)):
        clauses += [Or(Not(s[i-1][k-1]), Not(vars[i]))]

    clauses += [s[len(vars)-1][k-1]]    
    return clauses

def sum_k(vars, k):
    clauses = []
    nvars = [Not(var) for var in vars]
    clauses += at_most(vars, k)
    clauses += at_most(nvars, len(vars)-k)

    return clauses

######################## API ###########################

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

   

####################### Testing funcitons ##########################

# just to check the ouput of the function sum_k
def check_sum(n, k):
    p = get_fresh_vec(n)
    
    # notp = [Not(pi) for pi in p]
    vars = sum_k(p, k)
    # vars += at_most(notp, n-k) 

    sol = Solver()
    sol.add(And(vars))

    if sat == sol.check():
        m = sol.model()
        for pi in p:
            print(pi, m[pi])

def printit():
    global n, k
    print(n, k)