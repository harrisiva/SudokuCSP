import math
import copy

class Variable:
    def __init__(self,name,i,j,value,domain):
        self.name = name #  String to represent the name of the node (in the map example)
        self.value = value 
        self.domain = domain # Domain of the values the list can hold (initiliazed with the CSP Declared variable)
        self.i,self.j = i,j
        return
    def __str__(self):
        return f'{self.name}|{self.value}|{self.domain}'

class Graph:
    def __init__(self):
        self.edges:list = [] # List of edges
        self.nodes: list = []
        return
        
    def add_edge(self,from_node:Variable,to_node:Variable,constraint:list):
        # AC-3 CSP uses two way directed edges
        self.edges.append([from_node,to_node,constraint])

        # update list of nodes (check if node exists, if not true, append to list of nodes)
        node_exists = False
        for node in self.nodes:
            if from_node.name==node.name:
                node_exists = True
        if node_exists==False: 
            self.nodes.append(from_node)
    
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


def revise(edge, board:list): 
    # Set up the variables
    xi:Variable = edge[0]
    xiOriginal,constraints,revised = copy.deepcopy(xi.value), edge[2], False

    # Make consistent (i.e., validate constraints and trim xi's domain)
    domain_copy = copy.deepcopy(xi.domain) # Removals will be done to this list (as the original will be iterated on)
    for x in xi.domain:
        board[xi.i][xi.j]=x # Temporarily set the cell to hold x (for constraint evaluation purposes)
        for constraint in constraints: 
            if eval(constraint)==False: # Since the constraints for this CSP are alldiff based, remove x if any of the constraints are not met
                if x in domain_copy: domain_copy.remove(x)

    # Update xi's domain if a removal function was called and update revised value based on the latter
    if len(domain_copy)!=len(xi.domain):
        xi.domain=copy.deepcopy(domain_copy)
        revised = True
    
    board[xi.i][xi.j] = copy.deepcopy(xiOriginal) # Reset the cell's value
    return revised

def ac3(csp:CSP, board:list): # NOTE: AC-3 is fine, there are no issues with it
    queue:list = [edge for edge in csp.graph.edges] # add all the arcs (edges) from the csp's graph to the "queue"
    while len(queue)>0:
        arc = queue.pop() # order is irrelevant since it is commutative
        if revise(arc,board): # if there were any x in the from nodes domain that would never work with the to domain and was therefore trimmed
            if len(arc[0].domain)==0: return False # if no value in x, can be used as a consistent value with arc[0] with relation to arc[1], return false to indiciate that the problem is not solvable
            for edge in csp.graph.edges:  # Find all neighbots to arc[0] <- find edges that have edge[1]==arc[0] and add them back to the queue
                if edge[1]==arc[0]: queue.append(edge)
    return True


if __name__=='__main__': #To test AC-3 with the sqrt constraint example from m5-csp slide 17
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