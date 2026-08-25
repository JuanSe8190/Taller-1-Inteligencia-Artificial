from world.game import GameStateData
from world.station_rules import StationRules


class StationState:
    """
    A StationState specifies the full state of the station mission:
    - Robot position
    - Mission objects remaining
    - Terrain layout
    """

    def __init__(self, prevState=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState is not None:
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy(self):
        state = StationState(self)
        state.data = self.data.deepCopy()
        return state

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        return hasattr(other, "data") and self.data == other.data

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        return hash(self.data)

    def __str__(self):
        return str(self.data)

    def initialize(self, layout):
        """
        Creates an initial mission state from a layout.
        """
        self.data.initialize(layout)

    def getLegalActions(self):
        """
        Returns the legal actions for the robot.
        """
        if self.isWin() or self.isLose():
            return []

        # Get legal moves based on walls
        return StationRules.getLegalActions(self)

    def generateSuccessor(self, action):
        """
        Returns the successor state after the robot takes the action.
        """
        if self.isWin() or self.isLose():
            raise Exception("Can't generate a successor of a terminal state.")

        carriedModuleBeforeMove = self.data.hasModule

        # Copy current state
        state = StationState(self)

        # Apply action
        StationRules.applyAction(state, action)

        # Update cumulative cost according to the active mission.
        x, y = state.getRobotPosition()
        state.data.cumulativeCost += self._getStepCost(
            (x, y), carriedModuleBeforeMove
        )

        return state

    def _getStepCost(self, position, carriedModuleBeforeMove):
        """
        Returns the animation cost for one movement.
        """
        if self.data.missionType == "systems":
            return 1

        baseCost = self.data.layout.getTerrainCost(position[0], position[1])

        if self.data.missionType == "module" and carriedModuleBeforeMove:
            return 2 * baseCost

        return baseCost

    def getRobotState(self):
        """
        Returns an AgentState object for the robot.
        """
        return self.data.agentStates[0].copy()

    def getRobotPosition(self):
        """
        Returns the (x, y) position of the robot.
        """
        return self.data.agentStates[0].getPosition()

    def getNumAgents(self):
        return len(self.data.agentStates)

    def getLegacyTargets(self):
        """
        Returns the legacy target grid used by older S-based layouts.
        """
        return self.data.legacyTargets

    def getLegacyTargetsAsList(self):
        """
        Returns positions of legacy S-based targets.
        """
        return self.data.legacyTargets.asList()

    def getNumLegacyTargets(self):
        """
        Returns the number of remaining legacy S-based targets.
        """
        return self.data.legacyTargets.count()

    def getMissionType(self):
        """
        Returns the active mission type inferred from the layout.
        """
        return self.data.missionType

    def getDiagnosticTerminal(self):
        """
        Returns the diagnostic terminal position.
        """
        return self.data.diagnosticTerminal

    def getControlPosition(self):
        """
        Returns the control center position.
        """
        return self.data.controlPosition

    def getModulePosition(self):
        """
        Returns the energy module position.
        """
        return self.data.modulePosition

    def hasModule(self):
        """
        Returns True if the robot already picked up the module.
        """
        return self.data.hasModule

    def getKitPosition(self):
        """
        Returns the repair kit position.
        """
        return self.data.kitPosition

    def hasKit(self):
        """
        Returns True if the robot already picked up the repair kit.
        """
        return self.data.hasKit

    def getPendingSystems(self):
        """
        Returns the systems that still need repair.
        """
        return self.data.pendingSystems

    def getRepairedCount(self):
        """
        Returns the number of repaired systems.
        """
        return self.data.repairedCount

    def getTotalSystems(self):
        """
        Returns the total number of systems in the mission.
        """
        return self.data.totalSystems

    def getWalls(self):
        """
        Returns a Grid of boolean wall indicators.
        """
        return self.data.layout.walls

    def hasWall(self, x, y):
        """
        Returns True if there's a wall at (x, y).
        """
        return self.data.layout.walls[x][y]

    def isLose(self):
        """
        Mission failed (not used in basic search).
        """
        return self.data._lose

    def isWin(self):
        """
        Mission complete.
        """
        return self.data._win

    def getTerrain(self, x, y):
        """
        Returns the terrain type at position (x, y).

        Terrain types:
        - ' ' or '.': Normal floor
        - '~': Water
        - '^': Rubble
        - '*': Fire
        """
        return self.data.layout.getTerrain(x, y)

    def getTerrainCost(self, x, y):
        """
        Returns the movement cost for position (x, y).

        Costs:
        - Normal floor: 1
        - Water: 2
        - Rubble: 3
        - Fire: 5
        """
        return self.data.layout.getTerrainCost(x, y)
