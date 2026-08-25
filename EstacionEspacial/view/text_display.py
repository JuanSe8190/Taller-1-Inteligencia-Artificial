import time
from algorithms.utils import nearestPoint

DRAW_EVERY = 1
SLEEP_TIME = 0
DISPLAY_MOVES = False
QUIET = False


class NullGraphics:
    """
    Null graphics for quiet mode (no visual output).
    Used when running with -q flag.
    """

    def initialize(self, state, isBlue=False):
        pass

    def update(self, state):
        pass

    def checkNullDisplay(self):
        return True

    def pause(self):
        time.sleep(SLEEP_TIME)

    def draw(self, state):
        print(state)

    def updateDistributions(self, dist):
        pass

    def finish(self):
        pass


class StationGraphics:
    """
    Text-based graphics for the station maintenance domain.
    Displays the station area in ASCII format with:
    - % for walls
    - D, M, C, K, T for mission objects
    - Terrain symbols (~, ^, *) for movement costs
    """

    def __init__(self, speed=None):
        self.deferExecutionSummary = True
        self.layout = None
        self.robotAgent = None
        self.lastState = None
        if speed is not None:
            global SLEEP_TIME
            SLEEP_TIME = speed

    def setSummaryContext(self, layout, robotAgent):
        """
        Store execution context so text mode can print the summary at the end.
        """
        self.layout = layout
        self.robotAgent = robotAgent

    def initialize(self, state, isBlue=False):
        """
        Initialize the display with the initial mission state.
        """
        self.lastState = state
        self.draw(state)
        self.pause()
        self.turn = 0
        self.agentCounter = 0

    def update(self, state):
        """
        Update the display after each agent move.
        In this station mission, we typically only have one robot.
        """
        self.lastState = state
        numAgents = len(state.agentStates)
        self.agentCounter = (self.agentCounter + 1) % numAgents
        drewState = False
        if self.agentCounter == 0:
            self.turn += 1
            if DISPLAY_MOVES:
                # Display robot position, cost, and mission status.
                try:
                    robot_pos = nearestPoint(state.agentStates[0].getPosition())
                    cost = getattr(state, "cumulativeCost", 0)
                    print(
                        "%4d) R: %-8s" % (self.turn, str(robot_pos)),
                        "| Costo: %-5d" % cost,
                        "| %s" % state.getMissionStatusText(),
                    )
                except Exception:
                    # Fallback if mission status is not available.
                    cost = getattr(state, "cumulativeCost", 0)
                    print(
                        "%4d) Turno %d | Costo: %d" % (self.turn, self.turn, cost)
                    )
            if self.turn % DRAW_EVERY == 0:
                self.draw(state)
                drewState = True
                self.pause()
        if (state._win or state._lose) and not drewState:
            self.draw(state)

    def pause(self):
        """
        Pause between display updates.
        """
        if SLEEP_TIME < 0:
            input("Presione Enter para continuar...")
        else:
            time.sleep(SLEEP_TIME)

    def draw(self, state):
        """
        Draw the current state to the console.
        Uses the state's __str__ method which displays:
        - Walls as %
        - Mission symbols as D, M, C, K, T
        - Robot direction as ^, v, <, >
        - Cost at the bottom
        """
        print(state)

    def finish(self):
        """
        Called when the mission ends.
        """
        state = getattr(self, "lastState", None)
        if state is None:
            return

        layout = self.layout if self.layout is not None else getattr(state, "layout", None)
        agent = self.robotAgent

        if layout is not None:
            print("RobotPositions:", layout.agentPositions)
            print("MissionSymbols:", self._missionSymbols(layout))

        if agent is not None:
            if getattr(agent, "usesHeuristic", False):
                print(
                    "[SearchAgent] using function %s and heuristic %s"
                    % (agent.functionName, agent.heuristicName)
                )
            else:
                print("[SearchAgent] using function " + agent.functionName)
            print("[SearchAgent] using problem type " + agent.problemName)

        missionType = getattr(state, "missionType", "unknown")
        print("Misión:", state.getObjectiveText())
        print("Tipo de misión:", missionType)

        if agent is not None and agent.searchTotalCost is not None:
            print(
                "Path found with total cost of %d in %.1f seconds"
                % (agent.searchTotalCost, agent.searchTime)
            )
            if agent.searchNodesExpanded is not None:
                print("Search nodes expanded: %d" % agent.searchNodesExpanded)

        if state._win:
            print("¡Misión completada! Costo: %d" % state.cumulativeCost)
        elif state._lose:
            print("Misión fallida. Costo: %d" % state.cumulativeCost)
        else:
            print("Misión detenida. Costo: %d" % state.cumulativeCost)

    def _missionSymbols(self, layout):
        """
        Return mission symbol positions in the same format used by main.py.
        """
        return {
            symbol: layout.getSymbolPositions(symbol)
            for symbol in ["D", "C", "M", "K", "T"]
        }
