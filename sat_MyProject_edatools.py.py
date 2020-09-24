""" IMPLEMENTING A NETLIST EQUIVALENCE CHECiER USING A SAT APPROACH """
""" SUBJECT : EDA ToolS-II
    Group members:
                     Sohaib Arif             Mr.Nr:454364
                     Muhammad Aashir Ayaz    Mr.Nr:448046
"""
import sys
import copy
def readNetlist(file):
    nets = int(file.readline())
    inputs  = file.readline().split()
    inputs.sort()
    outputs = file.readline().split()
    outputs.sort()

    # read mapping
    mapping = {}
    while True:
        line = file.readline().strip()
        if not line:
            break

        net,name = line.split()
        mapping[name] = int(net)

    # read gates
    gates = []
    for line in file.readlines():
        bits = line.split()
        gate = bits.pop(0)
        ports = list (map(int,bits))
        gates.append((gate,ports))
        
    return inputs,outputs,mapping,gates,nets
""" functions of characteristics equations for My CNF """
"""   fc,INV=(avb)(-a v-b)      """
def inv_f(_y):
    return [[_y[0], _y[1]], [-_y[0], -_y[1]]]
"""  fc,AND=(-av-bvc)(av-c)(bv-c)   """
def and_f(_y):
    return [[_y[0], -_y[2]], [_y[1], -_y[2]], [-_y[0], -_y[1], _y[2]]]
"""  fc,OR=(avbv-c)(-avc)(-bvc)   """
def or_f(_y):
    return [[-_y[0], _y[2]], [-_y[1], _y[2]], [_y[0], _y[1], -_y[2]]]
""" fc,XOR=(avbv-c)(-av-bv-c)(-avbvc)(av-bvc)  """
def xor_f(_y):
    return [[_y[0], _y[1], -_y[2]], [-_y[0], -_y[1], -_y[2]], [-_y[0], _y[1], _y[2]], [_y[0], -_y[1], _y[2]]]
""" fc,EQUAL=(-avb)(a v-b) """
def equal_f(_y):
    return [[_y[0], -_y[1]], [-_y[0], _y[1]]]
# after Xor gates to get results
def add_f(_y):
    return [finalout]

def Characteristic_f(equations, _y):
    if equations == "and":
        return and_f(_y)
    elif equations == "or":
        return or_f(_y)
    elif equations == "add":
        return add_f(_y)
    elif equations == "xor":
        return xor_f(_y)
    elif equations == "inv":
        return inv_f(_y)
    elif equations == "equiv":
        return equal_f(_y)
    # Above My cnf chrateristics equations  completed.
 
""" My functions for DAVIS PUTNAM ALGORITHM """
# heuristics Function
""" apply unit clause rule to cnf until myheuristics 
            not applicable anymore """
def myheu(cnf_myheu):
    for i in cnf_myheu:
        if len(i) == 1 and i[0] > 0: # if positive unity clause found
            turthtable[abs(i[0])] = 1  # here set value 1 for that literal remove from clause.
            cnf_myheu.remove(i)
            for clause in reversed(cnf_myheu): # loop start from bottom
                for literal in clause:
                    if abs(literal) == i[0]:
                        if literal > 0: # means positive "1" so remove clause
                            cnf_myheu.remove(clause)
                        elif literal < 0: # means nagative "-1" so remove only literal
                            clause.remove(literal)

        elif len(i) == 1 and i[0] < 0: # for negative unity clause
            turthtable[abs(i[0])] = 0 # set value "0"
            cnf_myheu.remove(i)
            for clause in reversed(cnf_myheu):
                for literal in clause:
                    if abs(literal) == abs(i[0]):
                        if literal > 0: # means "1" which value "0" so remove only that literal
                            clause.remove(literal)
                        elif literal < 0: # means "-1" which value "1" so remove clause
                            cnf_myheu.remove(clause)
    for i in cnf_myheu:
        if len(i) == 1:
            myheu(cnf_myheu)
    return cnf_myheu
""" Davis Putnam Theorem """
def dp(cnf_dp):
    # heuristics
    cnf_from_myheu = myheu(cnf_dp)
    
    return terminal_condition(cnf_dp)

def terminal_condition(cnf_from_myheu):   
    # Terminal Conditions
    if len(cnf_from_myheu) == 0: # if there is No any clause in cnf
        return True # solution found
    
    elif len(cnf_from_myheu) > 0: # else finding empty clause
        for i in cnf_from_myheu:
            if len(i) == 0:
                return False # return No solution found

        return backtracking(cnf_from_myheu)

def backtracking(cnf_from_myheu):
    # Backtracking
    variable = abs(cnf_from_myheu[-1][-1])
    cnf_old = copy.deepcopy(cnf_from_myheu)
        # for negative variable
    cnf_from_myheu.append([-variable])
    result1 = dp(cnf_from_myheu)
        # for positive variable
    if not result1:
            cnf_old.append([variable])
            result1= dp(cnf_old)
    return result1       
        

# Here starts my code, like the main function in C++

#read netlist
netlist1_path = r'C:\eda_project\xor2_nand.net'
netlist2_path = r'C:\eda_project\adder4_rc.net'
inputs1, outputs1, mapping1, gates1, nets1  = readNetlist(open(netlist1_path,"r"))
inputs2, outputs2, mapping2, gates2, nets2  = readNetlist(open(netlist2_path,"r"))
""" Here My Meiter circuit starts """
# Mapping 2 updating by adding nets 1 in all wires.
for i in mapping2:
    mapping2[i] = mapping2[i] + nets1
# now updating Gates2 with updated mapping2
for i in range(len(gates2)):
    if len(gates2[i][1]) == 2:
        for m in range(2):
            gates2[i][1][m] = gates2[i][1][m] + nets1
    else:
        for n in range(3):
            gates2[i][1][n] = gates2[i][1][n] + nets1
finalgates = gates1 + gates2
        
# adding Xor gate to Meiter Circuit.
finalout = []
for i in range(len(outputs1)):
    finalgates.append(('xor', [mapping1[outputs1[i]], mapping2[outputs2[i]], nets2+nets1+i+1]))
    finalout.append(nets2+nets1+i+1)
# Final Simple Add the Gates
    finalgates.append(('add',  finalout))
# joining inputs
for i in range(len(inputs1)):
    finalgates.append(( 'equiv', [mapping1[inputs1[i]], mapping2[inputs2[i]]] ))
    """ End OF meiter Circuit """
# here calling my cnf and printing
cnf = []
for gates_large in finalgates:
    cnf += Characteristic_f(gates_large[0], gates_large[1])
print(cnf)
# table dictionary
turthtable = {} 
finalresult = dp(cnf)
if finalresult == False:
    print(' CNF is not satisfiable hence given two circuits are equivalent')
elif finalresult == True:
    print('\n Solution found, CNF is satisfiable hence given two circuits are not equivalent \n',
    ' Counter example is: ','\n Inputs: \n',end='')
    for ans in inputs1:
        print(ans, '=', turthtable[mapping1[ans]])

    print('Outputs of netlist1: ', end='')
    for ans in outputs1:
        print(ans, '=', turthtable[mapping1[ans]])
 
    print('Outputs of netlist2: ', end='')
    for ans in outputs2:
        print(ans, '=', turthtable[mapping2[ans]])