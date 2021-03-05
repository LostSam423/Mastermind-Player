from z3 import *

########## To keep track of the propositional variables #########
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
THRESH = 20
TRUE_THRESH = 2
n = k = 0
moves = []

colors_present = []
color = 0
find_colors = True

pvs = []
clauses = []
org_to_sel = {}

unsat_count = 0
essential_clauses_count = 0
almost_true_clauses = []
clauses_outs = {}

r_count = 0
color_moves = 1

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
    global var_counter, n, k, moves, colors_present, find_colors, color, clauses, org_to_sel, pvs, unsat_count, essential_clauses_count, r_count, almost_true_clauses, THRESH, TRUE_THRESH, color_moves

    if(red == k):
        print(r_count, color_moves)
        return
    
    # print(n, k, find_colors)

    if (find_colors and red > 0 and white == 0):
        key = str(moves[len(moves)-1])

        ess = False
        if key in clauses_outs.keys():
            if clauses_outs[key] == True:
                pass
            elif clauses_outs[key].count(red) >= TRUE_THRESH:
                ess = True
                clauses_outs[key] = True
            else:
                clauses_outs[key] += [red]

        else:
            clauses_outs[key] = [red]

        if ess:
            colors_present.append((color, red))
            org_to_sel[color] = len(colors_present)-1
        
            total_ele = sum(list(map(lambda x: x[1], colors_present)))
            if( total_ele == k):
                find_colors = False

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

                essential_clauses_count = len(clauses)

                sol = Solver()
                sol.add(And(clauses))
                assert(sol.check() == sat)

                # print_model(sol.model())
                moves.append(get_move(sol.model()))
                return

            elif (total_ele > k):
                r_count += 1
                # color_moves +=1
                reset()
        else:
            color = (color-1)%n

    if(find_colors):
        # print("here")
        color = (color+1)%n
        moves.append([color]*k)
        color_moves +=1 


    else:
        # moves will contain colors from original set
        # pvs in last move

        ess = False
        key = str(moves[len(moves)-1])

        if key in clauses_outs.keys():
            if clauses_outs[key] == True:
                pass
            elif clauses_outs[key].count((red, white)) >= TRUE_THRESH:
                ess = True
                clauses_outs[key] = True
            else:
                clauses_outs[key] += [(red, white)]

        else:
            clauses_outs[key] = [(red, white)]

        if(red+white != k):
            unsat_count += 1


        sol = Solver()
        selected_pvs = []
        for i in range(k):
            last_move = moves[len(moves)-1]
            selected_pvs += [pvs[org_to_sel[last_move[i]]][i]]
        
        new = sum_k(selected_pvs, red)
        clauses += new
        if ess:
            almost_true_clauses += new

        sol.add(And(clauses))

        if(sol.check() == unsat):
            if(unsat_count >= THRESH):
                moves.append([0]*k)
                reset()
            else:
                clauses = clauses[:essential_clauses_count]
                clauses += almost_true_clauses
                unsat_count += 1
                sol = Solver()
                sol.add(And(clauses))

                # assert(sol.check() == sat)
                if(sol.check() == unsat):
                    moves.append([0]*k)
                    reset()
                else:
                    moves.append(get_move(sol.model()))

        else:
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

def reset():
    global var_counter, n, k, moves, colors_present, find_colors, color, clauses, org_to_sel, pvs, unsat_count, essential_clauses_count, almost_true_clauses, clauses_outs

    print("reset")
    var_counter = 0
    clauses = []
    color = 0
    find_colors = True
    unsat_count = 0
    org_to_sel = {}
    colors_present = []
    essential_clauses_count = 0

    almost_true_clauses = []
    clauses_outs = {}


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