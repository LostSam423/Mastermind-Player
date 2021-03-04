from z3 import *
import time

def find_minimal(graph, s, t):

    # def bfs(m):
    #     queue = []
    #     visited = {}
    #     for i in a.keys():
    #         visited[i] = False

    #     queue.append(s)
    #     visited[s] = True

    #     parent = {}
    #     found = False
    #     while queue:
    #         node = queue.pop(0)
    #         for i in a[node]:
    #             if visited[i] == False and is_true(m[e[(node, i)]]):
    #                 parent[i] = node
    #                 if(i == t):
    #                     found = True
    #                     break
    #                 queue.append(i)
    #                 visited[i] = True
    #         if(found):
    #             break
    #     return parent


    a = {} # adjacency list
    e = {} # propositional variables e[(i,j)] representing edges from i to j
    p = {} # propostional variables p[j] representing path from s to j
    
    t0 = time.time()
    for (i,j) in graph:
        if i in a.keys():
            a[i] += [j]
        else: 
            a[i] = [j]
            p[i] = Bool(f"p_{i}")

        if j in a.keys(): 
            a[j] += [i]
        else:
            a[j] = [i]
            p[j] = Bool(f"p_{j}")

        e[(i,j)] = Bool(f"e-{i}-{j}") 

    # print(a)

    # p = [Bool(f"p_{i}") for i in a.keys() if i!=s]
    # print(p)

    vs = [p[s]]
    
    # for i in a[s]:
        # vs += [Or(Not(e[(s,i)]), p[i])]

    for (i,j) in graph:
        vs += [Or(Not(p[i]), Not(e[(i,j)]), p[j])]
        vs += [Or(Not(p[j]), Not(e[(i,j)]), p[i])]

    # for j in a.keys():
    #     if(j == s):
    #         continue
    #     paths = []
    #     for nei in a[j]:
    #         if(nei > j):
    #             f = nei
    #             l = j
    #         else:
    #             f = j
    #             l = nei

    #         if(nei == s):
    #             paths += [e[(l,f)]]
    #         else:
    #             paths += [And(p[nei], e[(l, f)])]
        
    #     vs += [Or(paths) == p[j]]


    vs += [Not(p[t])]

    # print(vs)
    sol = Optimize()
    sol.add(And(vs))
    sol.maximize(Sum([If(e[edge],1,0) for edge in e.keys()]))
    # for edge_c in e.keys():
    #     sol.add_soft(e[edge_c])

    sol.check()
    m = sol.model()

    ans = 0
    for edge_c in e.keys():
        if is_false(m[e[edge_c]]):
            ans+=1

    f0 = time.time()
    # print(f0-t0)
    # p1 = Bool("p1")
    # p2 = Bool("p2")

    # sol = Optimize()
    # sol.add(p1==p2)
    # sol.add_soft(p1)
    # sol.add_soft(p2)

    # r = sol.check()
    # print(r)
    # print(sol.model())

    # while(sol.check() == sat):
    #     ans += 1
    #     m = sol.model()
    #     print(m)
    #     parent = bfs(m)
    #     print(parent)
    #     sol = Solver()
    #     sol.add(And(vs))
    #     break

    return ans