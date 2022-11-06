import math
import copy

class Variable:
    def __init__(self,name,value,domain):
        self.name = name #  String to represent the name of the node (in the map example)
        self.value = value 
        self.domain = domain # Domain of the values the list can hold (initiliazed with the CSP Declared variable)
        return
    def __str__(self):
        return f'{self.name}|{self.value}|{self.domain}'

class Graph:
    def __init__(self):
        self.nodes: int = 0 # Number of nodes
        self.edges:list = [] # List of edges
        return
        
    def add_edge(self,node1:Variable,node2:Variable,constraint:list):
        # AC-3 CSP uses two way directed edges
        self.edges.append([node1,node2,constraint])
        self.nodes+=1
        return
    
    def view_graph(self): # Print as a list of edges
        print('From|To|Constraint')
        for edge in self.edges:
            print(f'{edge[0].name}|{edge[1].name}|{edge[2]}')
        return

class CSP:
    def __init__(self, graph: Graph):
        self.variables=[] # Variable objects
        self.domain=[] # Domain for each variable or common, depending on the problem
        self.constaints=[] 
        self.graph = graph
        return
    def __str__(self):
        returnable = ''
        for variable in self.variables:
            returnable += f'{variable.name}: {variable.domain}\n'
        return returnable

def revise(edge): 
    xi:Variable = edge[0]
    xj:Variable = edge[1]
    constraint:str = edge[2]
    revised:bool = False # Set revised initially to be false
    
    # get a copy of xi's domain
    xi_domain_cpy = copy.deepcopy(xi.domain)

    for x in xi.domain: # itterate through the original xi domain
        consistent = False
        
        for y in xj.domain: # iterate through the domain of xj
            for a_constraint in constraint:
                if eval(a_constraint)==True: 
                    consistent = True # To check consistency, evaluate the constraint for the given edge, if true, that means the constraint is met                
        
        # if x can not be consistent with any values in the domain of y, remove x from xi's copied domain,
        if consistent!=True:
            xi_domain_cpy.remove(x)            

    # If the length of the original domain is 
    # not equal to the length of the copied domain, 
    # set revised to be true as the length of the 
    # original domain will change based on th removal of values.
    # and set xi.domain to be the same as the copy
    if len(xi_domain_cpy)!=len(xi.domain): 
        revised=True 
        xi.domain = copy.deepcopy(xi_domain_cpy)

    return revised

def ac3(csp:CSP):
    queue:list = [edge for edge in csp.graph.edges] # add all the arcs (edges) from the csp's graph to the "queue"
    while len(queue)>0:
        arc = queue.pop() # order is irrelevant since it is commutative
        if revise(arc): # if there were any x in the from nodes domain that would never work with the to domain and was therefore trimmed
            if len(arc[0].domain)==0: return False # if no value in x, can be used as a consistent value with arc[0] with relation to arc[1], return false to indiciate that the problem is not solvable
            for edge in csp.graph.edges:  # Find all neighbots to arc[0] <- find edges that have edge[1]==arc[0] and add them back to the queue
                if edge[1]==arc[0]: queue.append(edge)

    return True


if __name__=='__main__':
    # Test the Graph DS and AC-3 with slide 17 example
    CSP_domain = [0,1,2,3,4,5,6,7,8,9]
    # Create the variables with a variable name and a common domain
    x = Variable('X',-1,CSP_domain)
    y = Variable('Y',-1,CSP_domain)
    # Create the graph by inserting edges
    graph = Graph() # Initialize the graph object
    # Add the edges to the graph (with constraints)
    graph.add_edge(x,y,['x==math.sqrt(y)'])
    graph.add_edge(y,x,['(y*y)==x'])
    # Initializing CSP with the graph
    csp = CSP(graph)
    # Add the variables to the CSP
    csp.variables.append(x)
    csp.variables.append(y)
    csp.domain=CSP_domain # Set the common domain of values
    # Set the constraints (in this case, just copy them from the edges to the csp data structure)
    for edge in graph.edges: csp.constaints.append(edge[2])
    if ac3(csp): print(csp)