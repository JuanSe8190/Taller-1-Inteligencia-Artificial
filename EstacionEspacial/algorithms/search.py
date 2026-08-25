from algorithms.problems import SearchProblem
import algorithms.utils as utils
from world.game import Directions
from algorithms.heuristics import nullHeuristic


def tinyDiagnosticSearch(problem: SearchProblem):
    """
    Returns a hard-coded sequence of moves for the tinyDiagnostic layout.
    For any other station layout, the sequence of moves will be incorrect.
    """
    s = Directions.SOUTH
    e = Directions.EAST
    return [s, e, s, e, e, e, e, s, e, e, s, s, e, s, s, e, s, e, e, e, e, e, e, e]


def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    stack=utils.Stack()
    
    print("Start:", problem.getStartState())
    
    stack.push((problem.getStartState(),[]))
    
    visited=set()
    
    while not stack.isEmpty():
        state,actions=stack.pop()
        
        if state in visited:
            continue
        
        visited.add(state)
        
        if problem.isGoalState(state):
            return actions
        
        for successor, action, stepCost in problem.getSuccessors(state):
            
            if successor not in visited:
                stack.push((successor, actions + [action]))
                
    return []


def breadthFirstSearch(problem: SearchProblem):
    """
    Search the shallowest nodes in the search tree first.
    """
    queue=utils.Queue()
        
    print("Start:", problem.getStartState())
        
    queue.push((problem.getStartState(),[]))
        
    visited=set()
        
    while not queue.isEmpty():
        
        state,actions=queue.pop()
            
        if state in visited:
            continue
            
        visited.add(state)
            
        if problem.isGoalState(state):
            return actions
            
        for successor, action, stepCost in problem.getSuccessors(state):
                
            if successor not in visited:
                queue.push((successor, actions + [action]))
                    
    return []
    


def uniformCostSearch(problem: SearchProblem):
    """
    Search the node of least total cost first.
    """

    # TODO: Add your code here
    utils.raiseNotDefined()


def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """
    Search the node that has the lowest combined cost and heuristic first.
    """
    # TODO: Add your code here
    utils.raiseNotDefined()


# Abbreviations (you can use them for the -f option in main.py)
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
