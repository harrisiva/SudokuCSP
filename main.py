from constants import *
from copy import deepcopy as asvalue
import numpy as np
# MODEL 2

def viewBoard(variables, assignments):
    tempMat = [
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
    ]
    for variable in variables: tempMat[ROW_LETTER_AS_KEY[variable[0]]][int(variable[1])-1] = assignments[variable]
    print(np.array(tempMat))
    return

def gen_box_constraints():
    board = [
    [4,8,3, 9,2,1, 6,5,7],
    [9,6,0, 3,4,5, 8,0,1],
    [2,5,1, 8,7,6, 4,9,3],

    [5,4,8, 1,3,2, 9,7,6],
    [7,2,9, 5,0,0, 1,3,8],
    [1,0,6, 7,9,8, 2,0,5],

    [3,7,2, 6,8,9, 5,1,4],
    [0,1,0, 2,5,3, 7,6,9],
    [6,9,5, 4,1,7, 0,8,2],
    ]
    def gen_box_constraints_helper(x, y, w, z):
        with open("map_constraints2.txt","a+") as f:
            for i in range(x, y):
                for j in range(w, z):
                    for k in range(x,y):
                        for l in range(w, z):
                            if (k,l) != (i, j):
                                f.write(f'{ROW_INDEX_AS_KEY[i]}{j+1}!={ROW_INDEX_AS_KEY[k]}{l+1}\n')

    gen_box_constraints_helper(0,3, 0,3)
    gen_box_constraints_helper(0,3, 3,6)
    gen_box_constraints_helper(0,3, 6,9)
    gen_box_constraints_helper(3,6, 0,3)
    gen_box_constraints_helper(3,6, 3,6)
    gen_box_constraints_helper(3,6, 6,9)
    gen_box_constraints_helper(6,9, 0,3)
    gen_box_constraints_helper(6,9, 3,6)
    gen_box_constraints_helper(6,9, 6,9)

def loadSudoku(board):
    variables = []
    indexes = {}
    domains = {}
    assignments = {}
    constraints = {}

    with open('map_constraints.txt','r') as file: BOXCONSTRAINTS=[line.replace('\n','') for line in file.readlines()] # Load box constraints from map_constraints file
    for i in range(0,len(board),1):
        for j in range(0,len(board[i]),1):
            name = f'{ROW_INDEX_AS_KEY[i]}{j+1}' # j+1 because we are mapping 0 index as 1
            value = board[i][j]
            domain = asvalue(INITIAL_STANDARD_DOMAIN) if value==0 else [value]
            constraints_list = []

            # Update constraints list to the contain the value==assigned_value constraint
            if value!=0: constraints_list.append(f'{name}=={value}')
            
            # Generate the alldiff constraints for this variable
            for row in range(len(board)):
                for col in range(len(board[row])):
                    if row == i and col!=j:
                        constraints_list.append(f'{name}!={ROW_INDEX_AS_KEY[row]}{col+1}')
                    if col == j and row != i:
                        constraints_list.append(f'{name}!={ROW_INDEX_AS_KEY[row]}{col+1}')

            # Retrive the box constraints for this variable (where this variable is the from node)
            for constraint in BOXCONSTRAINTS: 
                if name in constraint[:2]: constraints_list.append(constraint)

            variables.append(name)
            indexes[name]=[i,j]
            domains[name]=domain
            assignments[name]=value #if value!=0: assignments[name]=value # NOTE: Append variable:value only if variable has a value assigned to it (meaning !=0 since 0's are blank)
            constraints[name]=constraints_list

    return variables, indexes, domains, assignments, constraints

def evaluate_constraint(constraint:str,assignments:dict):
    x_key:str = constraint[0:2]
    y_key:str = constraint[4:]
    if y_key.isnumeric():
        return assignments[constraint[0:2]]==int(y_key)
    return assignments[constraint[0:2]]!=assignments[constraint[4:]]

# Revise given the variable_name, domain, and assignment (Modified Revise)
def revise(variable_name, domains, constraints, assignments):
    variable_domain = asvalue(domains[variable_name])
    variable_constraints = constraints[variable_name]
    original_variable_value = asvalue(assignments[variable_name])

    revised = False
    for domain_value in variable_domain: # iterate through this variables domain
        assignments[variable_name]=domain_value # set the current value in iteration as the assignment (value for the variable)
        for constraint in variable_constraints:
            if evaluate_constraint(constraint,assignments)==False: # if it is ever false
                if domain_value in domains[variable_name]: domains[variable_name].remove(domain_value)
                revised = True

    # Reset the assignment to hold the variables original value
    assignments[variable_name]=original_variable_value
    return revised

# Call revise to trim the domain of every variable (Modified AC-3)
def ac3(variables,domains,assignments,constraints):
    for variable in variables:
        revise(variable,domains,constraints,assignments)
        if len(domains[variable])==0: return False
    return True

def is_consistent(variable,value,assignments,constraints): # Adds the assignment to copy (as value) of the assignments dictionary and checks if all the constraints hold true, if not, returns false, else returns true
        # set the variables value in assignments (copy as value) to be the given value
        assignments_copy:dict = asvalue(assignments) # All changes as made on this (as its a copy by value), not the original assignments dictionary
        assignments_copy[variable]=value
        # check if it is consistent with the cosntraints with the help of the evalute constraint function
        for constraint in constraints[variable]:
            if evaluate_constraint(constraint,assignments_copy)==False: return False
        return True

def updateAssignments(variables,assignments,domains,constraints):
    for variable in variables:
        if len(domains[variable])==1: 
            if is_consistent(variable,domains[variable][0],assignments,constraints):
                assignments[variable] = domains[variable][0]
    return

def updateDomain(variables,assignments,domains): # if any variable has a value assigned to it, update its domain to only carry that value
    for variable in variables:
        if assignments[variable]!=0:
            domains[variable]=[assignments[variable]]
    return

def updateConstraints(variables,assignments,constraints): # for any assigned value, set a new constraint where the variable[value]==value
    for variable in variables:
        if assignments[variable]!=0:
            if f'{variable}=={assignments[variable]}' not in constraints[variable]: constraints[variable].append(f'{variable}=={assignments[variable]}')
    return

def updateAll(variables,domains,assignments,constraints):
    updateDomain(variables,assignments,domains)
    updateAssignments(variables,assignments,domains, constraints)
    updateConstraints(variables,assignments,constraints)
    return

# Utility functions for backtracking
def is_complete(assignments): # Check if every variable has an assignment (the dictionary has a default value of 0 for each assignment)
    for assignment in assignments: 
        if assignments[assignment]==0: return False
    return True

def select_unassigned_variable(variables, domains): # For selecting an unassigned variable using the MRV heuristic
    minimum = 9 # Domains can have a max of 8 values
    mrv_variable = None # Initialize mrv_variable as None
    for variable in variables: # Loop through the list of variables
        if len(domains[variable])!=1 and len(domains[variable])<minimum: # if the vairable has a domain greater than 1 and smaller than the minimum
            minimum = len(domains[variable]) # set the length of the variables domain as the minimum (length of the smallest domain <- updated every iteration)
            mrv_variable = variable # set the variable as the MRV variable
    return mrv_variable

# NOTE: Verified that infer does not change the parameters states but there
def infer(variables,domains,assignments,constraints): # Returns inferences as a dict and the updated (copy as value) domains, assignments, and constraints
    # create a copy as value of everything
    variables_copy = asvalue(variables)
    domains_copy = asvalue(domains)
    assignments_copy = asvalue(assignments)
    constraints_copy = asvalue(constraints)

    updateAll(variables_copy,domains_copy,assignments_copy,constraints_copy)

    # call ac3
    if ac3(variables_copy,domains_copy,assignments_copy,constraints_copy):

        updateAll(variables_copy,domains_copy,assignments_copy,constraints_copy)  # update all the copies based on fully assigned variables (assignments[variable]!=0)
        # Get the difference between assignments and assignments copy to create a dictionary of inferences
        inferences = {}
        for variable in variables: # the length and contents of variables_copy always matches variables
            if assignments[variable]!=assignments_copy[variable]: inferences[variable]=assignments_copy[variable]
                
        return inferences, domains_copy, constraints_copy, assignments_copy #return the inferences dictionary, new domain, constraints, and assignments
    return False,False,False,False, # if AC-3 fails, return false

# For backtracking, rather than taking instances of ds's, we just take the dictionaries (modified, not consistent with slides psuedocode)
def backtrack(variables,domains,assignments,constraints): # def backtrack(the four variables without the indexes)

    # Success base case: Returns the given assignments
    if is_complete(assignments): return domains,assignments,constraints

    variable = select_unassigned_variable(variables, domains) # select unassigned variable with the MRV heuristic
            
    original_value = asvalue(assignments[variable])
            
    for value in domains[variable]: # for each value in the selected variables domain

        if is_consistent(variable,value,assignments,constraints): # check if the value is consistent with the current assignments

            assignments[variable]=value # add var=value to the assignment by upadting the variables assignment
            inferences, domains_copy, constraints_copy, assignments_copy = infer(variables, domains, assignments, constraints)
                    
            if inferences!=False: # if inferences did not fail (NOTE: No need to add inferences to assignment as they are already in assignments_copy)

                domains_copy, assignments_copy, constraints_copy = backtrack(variables,domains_copy,assignments_copy,constraints_copy) # call backtracking again with the updated (copies) of domains, assignments, and constraints 
                if domains_copy!=False:
                    return domains_copy, assignments_copy, constraints_copy # The assignments and othe fields returned by the last infer (ac-3) call

    assignments[variable] = original_value # Remove the variable from the assignments (by reseting the assignment to hold the original value for the variabel <- will it be anything other than 0?). The inferences need not be removed since they are not present in assignments and only present in assignments_copy (same for all the domains)
                
    return False, False, False

if __name__=='__main__':
    variables, indexes, domains, assignments, constraints = loadSudoku(RANDOM_BOARD)
    if ac3(variables,domains,assignments,constraints):
        updateAll(variables,domains,assignments,constraints) # Updates the given domains, assignments, constraints to match the given variables value assignment (if it is complete)

        # Check (based) on assignments if the puzzle is solved
        solved = True
        for variable in variables: solved = False if assignments[variable]==0 else solved

        print(f'Solved with AC-3 alone: {solved}')
        viewBoard(variables,assignments)
        if solved==False:
            print("Executing backtracking with AC-3 as the inference function")

            backtracked_domains, backtracked_assignments,backtracked_constraints = backtrack(variables, domains, assignments, constraints)

            print()
            if backtracked_domains!=False:
                print("Board after backtracking:")
                viewBoard(variables, backtracked_assignments)
            else: print("Backtracking Failed. Puzzle is not solvable using backtracking")
    else:
        print("Puzzle state is unsolvable")