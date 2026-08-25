import time
from world.game import Directions, Agent
import algorithms.search as search
import algorithms.problems as problems
import algorithms.heuristics as heuristics


class SearchAgent(Agent):
    """
    General search agent that uses a search algorithm to find paths.

    The agent:
    1. Creates a search problem
    2. Runs a search algorithm to find a path
    3. Executes the path step by step

    Don't modify this class - it's the framework that calls your code.
    """

    def __init__(
        self,
        fn="tinyDiagnosticSearch",
        prob="DiagnosticProblem",
        heuristic="nullHeuristic",
        deferOutput=False,
    ):
        """
        fn: Name of search function (dfs, bfs, ucs, astar)
        prob: Name of problem class
        heuristic: Name of heuristic function (for A*)
        """
        self.functionName = fn
        self.problemName = prob
        self.heuristicName = heuristic
        self.deferOutput = deferOutput
        self.usesHeuristic = False
        self.searchTotalCost = None
        self.searchTime = None
        self.searchNodesExpanded = None

        # Get the search function from the name
        if fn not in dir(search):
            raise AttributeError(fn + " is not a search function in search.py.")
        func = getattr(search, fn)

        # Check if this search function uses a heuristic
        if "heuristic" not in func.__code__.co_varnames:
            if not self.deferOutput:
                print("[SearchAgent] using function " + fn)
            self.searchFunction = func
        else:
            # For A*, we need to bind the heuristic
            self.usesHeuristic = True
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(heuristics):
                heur = getattr(heuristics, heuristic)
            else:
                raise AttributeError(heuristic + " is not a function in heuristics.py")
            if not self.deferOutput:
                print("[SearchAgent] using function %s and heuristic %s" % (fn, heuristic))
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the problem class
        if prob not in dir(problems):
            raise AttributeError(prob + " is not a search problem type in problems.py.")
        self.searchType = getattr(problems, prob)
        if not self.deferOutput:
            print("[SearchAgent] using problem type " + prob)

    def registerInitialState(self, state):
        """
        Called once at the start. This is where we plan the path.
        """
        if self.searchFunction is None:
            raise Exception("No search function provided for SearchAgent")

        starttime = time.time()
        problem = self.searchType(state)  # Create the search problem
        self.actions = self.searchFunction(problem)  # Find path using search algorithm

        if self.actions is None:
            self.actions = []

        totalCost = problem.getCostOfActions(self.actions)
        elapsed = time.time() - starttime
        self.searchTotalCost = totalCost
        self.searchTime = elapsed
        if not self.deferOutput:
            print(
                "Path found with total cost of %d in %.1f seconds"
                % (totalCost, elapsed)
            )
        if "_expanded" in dir(problem):
            self.searchNodesExpanded = problem._expanded
            if not self.deferOutput:
                print("Search nodes expanded: %d" % problem._expanded)

    def getAction(self, state):
        """
        Returns the next action in the planned path.
        """
        if "actionIndex" not in dir(self):
            self.actionIndex = 0

        i = self.actionIndex
        self.actionIndex += 1

        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP
