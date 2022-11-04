class Variable:
    def __init__(self,name,domain):
        self.name = name #  String to represent the name of the node (in the map example)
        self.value = -1 # Default ==-1 which means its not holding any colors
        self.domain = domain # Domain of the values the list can hold (initiliazed with the CSP Declared variable)
        return
    
class Graph:
    def __init__(self):
        self.nodes: int = 0 # Number of nodes
        self.edges:list = [] # List of edges
        return
        
    def add_edge(self,node1,node2,constraint):
        # AC-3 CSP uses two way directed edges
        self.edges.append([node1,node2,constraint])
        self.nodes+=1
        return
    
    def view_graph(self): # Print as a list of edges
        print('From|To|Constraint')
        for edge in self.edges:
            print(f'{edge[0].name}|{edge[1].name}|{eval(edge[2])}')
        return


class CSP:
    def __init__(self, graph: Graph):
        self.variables=[] # Variable objects
        self.domain=[] # Domain for each variable or common, depending on the problem
        self.constaints=[] 
        self.graph = graph
        return


# Test the Graph DS with the Coloring graph
CSP_domain = [0,1,2] # 0: Red, 1: Green, 2: Blue
# Create the variables for the different states in AU
wa = Variable('WA',CSP_domain)
nt = Variable('NT',CSP_domain)
q = Variable('Q',CSP_domain)
sa = Variable('SA',CSP_domain)
nsw = Variable('NSW',CSP_domain)
v = Variable('V',CSP_domain)
t = Variable('T',CSP_domain)
# Create the graph by inserting edges
graph = Graph() # Initialize the graph object

# Add the edges
graph.add_edge(wa,nt,'wa.value!=nt.value')
graph.add_edge(wa,sa,'wa.value!=sa.value')

graph.add_edge(nt,wa,'nt.value!=wa.value')
graph.add_edge(nt,sa,'nt.value!=sa.value')
graph.add_edge(nt,q,'nt.value!=q.value')


graph.add_edge(sa,wa,'sa.value!=wa.value')
graph.add_edge(sa,nt,'sa.value!=nt.value')
graph.add_edge(sa,q,'sa.value!=q.value')
graph.add_edge(sa,nsw,'sa.value!=nsw.value')
graph.add_edge(sa,v,'sa.value!=v.value')

graph.add_edge(q,nt,'q.value!=nt.value')
graph.add_edge(q,nsw,'q.value!=nsw.value')
graph.add_edge(q,sa,'q.value!=sa.value')

graph.add_edge(nsw,q,'nsw.value!=q.value')
graph.add_edge(nsw,sa,'nsw.value!=sa.value')
graph.add_edge(nsw,v,'nsw.value!=v.value')

graph.add_edge(v,nsw,'v.value!=nsw.value')
graph.add_edge(v,sa,'v.value!=sa.value')


# Initializing CSP with the constraints
csp = CSP(graph)
# Add the variables
csp.variables.append(wa)
csp.variables.append(nt)
csp.variables.append(sa)
csp.variables.append(q)
csp.variables.append(v)
csp.variables.append(t)

# Set the common domain of values
csp.domain=CSP_domain

# Set the constraints (in this case, just copy them from the edges to the csp data structure)
for edge in graph.edges: csp.constaints.append(edge[2])


def revise(edge): # edge[0]=Xi and edge[1]=Xj
    revised = False
    for x in edge[0].domain:
        to_remove = True
        edge[0].value = x # set  x to be the value of the node (edge[0]) 
        for y in edge[1].domain:
            edge[1].value = y # set y to be the value of the node (edge[1])
            if eval(edge[2]):
                to_remove = False
                break # loop through, if at any point the constraint between x and y is true, go to the next value of x
        if to_remove==True:
            edge[0].domain.remove(x)
            revised = True
    edge[0].value,edge[1].value = -1,-1 # reset both the edges to hold the default values
    return revised

def ac3(csp:CSP):
    queue:list = [edge for edge in csp.graph.edges] # add all the arcs (edges) from the csp's graph to the "queue"
    while len(queue)!=0:
        arc = queue.pop()
        if revise(arc):
            print(arc[0].name,':',arc[2])
    return

ac3(csp)
