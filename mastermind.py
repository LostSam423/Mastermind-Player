import random
from z3 import *

# supplying new propositional variables
var_counter = 0
def count():
    global var_counter
    count = var_counter
    var_counter = var_counter +1
    return str(count)

def get_fresh_bool(suff = ""):
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

    # clauses += [s[len(vars)-1][k-1]]    
    return clauses

def sum_k(vars, k):
    clauses = []
    nvars = [Not(var) for var in vars]
    clauses += at_most(vars, k)
    clauses += at_most(nvars, len(vars)-k)

    return clauses

######################## API ###########################

# static variables for 1 instance of the game
n = k = 0
moves = []

colors_present = []
color = 0
find_colors = True

pvs = []
clauses = []
org_to_sel = {}

def initialize(num, sel):
    global n, k, moves
    n = num
    k = sel
    moves = []
    guess = [0]*k

    moves.append(guess)

def get_second_player_move():
    global n, k, moves

    return moves[len(moves)-1]

def put_first_player_response(red, white):
    global var_counter, n, k, moves, colors_present, find_colors, color, clauses, org_to_sel, pvs

    if(red == k):
        return
    
    # print(n, k, find_colors)

    if (find_colors and red > 0 and white == 0):
        colors_present.append((color, red))
        org_to_sel[color] = len(colors_present)-1

        if(sum(list(map(lambda x: x[1], colors_present))) == k):
            find_colors = False
            var_counter = 0
            clauses = []
            pvs = [get_fresh_vec(k) for _ in range(len(colors_present))]
            # print(pvs)
            # print(colors_present)
            for i in range(len(colors_present)):
                clauses += sum_k(pvs[i], colors_present[i][1])

            for j in range(k):
                list_pvs = []
                for i in range(len(colors_present)):
                    list_pvs += [pvs[i][j]]
                clauses += sum_k(list_pvs, 1)

            sol = Solver()
            sol.add(And(clauses))
            assert(sol.check() == sat)

            # print_model(sol.model())
            moves.append(get_move(sol.model()))

            return


    if(find_colors):
        # print("here")
        color = (color+1)%n
        moves.append([color]*k)


    else:
        # moves will contain colors from original set
        # pvs in last move
        selected_pvs = []
        for i in range(k):
            last_move = moves[len(moves)-1]
            selected_pvs += [pvs[org_to_sel[last_move[i]]][i]]
        
        clauses += sum_k(selected_pvs, red)
        sol = Solver()
        sol.add(And(clauses))

        assert(sol.check() == sat)
        ## haven't considered lying cases yet
        moves.append(get_move(sol.model()))


def get_move(model):
    global k, colors_present, pvs

    move = [0]*k
    for i in range(len(colors_present)):
        for j in range(k):
            if is_true(model[pvs[i][j]]):
                # print("here")
                move[j] = colors_present[i][0]
    
    return move

   

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

def print_model(model):
    global pvs, n, k, colors_present
    
    for i in range(len(colors_present)):
        for j in range(k):
            print(model[pvs[i][j]], end=" ")
        print("")