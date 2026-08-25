from algorithms.utils import raiseNotDefined, nearestPoint
import time
import traceback
import sys


class Agent:
    """
    An agent that takes actions in a StationState.
    """

    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a StationState and must return an action
        from Directions.{North, South, East, West, Stop}
        """
        raiseNotDefined()

    def registerInitialState(self, state):
        """
        This method is called before any moves are made.
        It is optional, and agents may leave it out if they don't need it.
        """
        pass


class Directions:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    STOP = "Stop"

    LEFT = {NORTH: WEST, SOUTH: EAST, EAST: NORTH, WEST: SOUTH, STOP: STOP}

    RIGHT = dict([(y, x) for x, y in LEFT.items()])

    REVERSE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST, STOP: STOP}


class Configuration:
    """
    A Configuration holds the (x,y) coordinate of a character, along with its
    traveling direction.

    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically.  Therefore, north is the direction of increasing y, or (0,1).
    """

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction

    def getPosition(self):
        return self.pos

    def getDirection(self):
        return self.direction

    def isInteger(self):
        x, y = self.pos
        return x == int(x) and y == int(y)

    def __eq__(self, other):
        if other is None:
            return False
        return self.pos == other.pos and self.direction == other.direction

    def __hash__(self):
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 13 * y)

    def __str__(self):
        return "(x,y)=" + str(self.pos) + ", " + str(self.direction)

    def generateSuccessor(self, vector):
        """
        Generates a new configuration reached by translating the current
        configuration by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.

        Actions are movement vectors.
        """
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        if direction == Directions.STOP:
            direction = self.direction  # There is no stop direction
        return Configuration((x + dx, y + dy), direction)


class AgentState:
    """
    AgentStates hold the state of an agent (configuration, speed, etc).
    """

    def __init__(self, startConfiguration):
        self.start = startConfiguration
        self.configuration = startConfiguration
        self.numCarrying = 0
        self.numReturned = 0

    def __str__(self):
        return str(self.configuration)

    def __eq__(self, other):
        if other is None:
            return False
        return self.configuration == other.configuration

    def copy(self):
        state = AgentState(self.start)
        state.configuration = self.configuration
        state.numCarrying = self.numCarrying
        state.numReturned = self.numReturned
        return state

    def getPosition(self):
        if self.configuration is None:
            return None
        return self.configuration.getPosition()

    def getDirection(self):
        return self.configuration.getDirection()


class Grid:
    """
    A 2-dimensional array of objects backed by a list of lists.  Data is accessed
    via grid[x][y] where (x,y) are positions on a map with x horizontal,
    y vertical and the origin (0,0) in the bottom left corner.

    The __str__ method constructs an output that is oriented like a game board.
    """

    def __init__(self, width, height, initialValue=False, bitRepresentation=None):
        if initialValue not in [False, True]:
            raise Exception("Grids can only contain booleans")
        self.CELLS_PER_INT = 30

        self.width = width
        self.height = height
        self.data = [[initialValue for y in range(height)] for x in range(width)]
        if bitRepresentation:
            self._unpackBits(bitRepresentation)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        out = [
            [str(self.data[x][y])[0] for x in range(self.width)]
            for y in range(self.height)
        ]
        out.reverse()
        return "\n".join(["".join(x) for x in out])

    def __eq__(self, other):
        if other is None:
            return False
        return self.data == other.data

    def __hash__(self):
        base = 1
        h = 0
        for line in self.data:
            for i in line:
                if i:
                    h += base
                base *= 2
        return hash(h)

    def copy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g

    def deepCopy(self):
        return self.copy()

    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g

    def count(self, item=True):
        return sum([x.count(item) for x in self.data])

    def asList(self, key=True):
        list = []
        for x in range(self.width):
            for y in range(self.height):
                if self[x][y] == key:
                    list.append((x, y))
        return list

    def packBits(self):
        """
        Returns an efficient int list representation

        (width, height, bitPackedInts...)
        """
        bits = [self.width, self.height]
        currentInt = 0
        for i in range(self.height * self.width):
            bit = self.CELLS_PER_INT - (i % self.CELLS_PER_INT) - 1
            x, y = self._cellIndexToPosition(i)
            if self[x][y]:
                currentInt += 2**bit
            if (i + 1) % self.CELLS_PER_INT == 0:
                bits.append(currentInt)
                currentInt = 0
        bits.append(currentInt)
        return tuple(bits)

    def _cellIndexToPosition(self, index):
        x = index // self.height
        y = index % self.height
        return x, y

    def _unpackBits(self, bits):
        """
        Fills in data from a bit-level representation
        """
        cell = 0
        for packed in bits:
            for bit in self._unpackInt(packed, self.CELLS_PER_INT):
                if cell == self.width * self.height:
                    break
                x, y = self._cellIndexToPosition(cell)
                self[x][y] = bit
                cell += 1

    def _unpackInt(self, packed, size):
        bools = []
        if packed < 0:
            raise ValueError("must be a positive integer")
        for i in range(size):
            n = 2 ** (self.CELLS_PER_INT - i - 1)
            if packed >= n:
                bools.append(True)
                packed -= n
            else:
                bools.append(False)
        return bools


def reconstituteGrid(bitRep):
    if type(bitRep) is not type((1, 2)):
        return bitRep
    width, height = bitRep[:2]
    return Grid(width, height, bitRepresentation=bitRep[2:])


class Actions:
    """
    A collection of static methods for manipulating move actions.
    """

    # Directions
    _directions = {
        Directions.NORTH: (0, 1),
        Directions.SOUTH: (0, -1),
        Directions.EAST: (1, 0),
        Directions.WEST: (-1, 0),
        Directions.STOP: (0, 0),
    }

    _directionsAsList = _directions.items()

    TOLERANCE = 0.001

    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action

    reverseDirection = staticmethod(reverseDirection)

    def vectorToDirection(vector):
        dx, dy = vector
        if dy > 0:
            return Directions.NORTH
        if dy < 0:
            return Directions.SOUTH
        if dx < 0:
            return Directions.WEST
        if dx > 0:
            return Directions.EAST
        return Directions.STOP

    vectorToDirection = staticmethod(vectorToDirection)

    def directionToVector(direction, speed=1.0):
        dx, dy = Actions._directions[direction]
        return (dx * speed, dy * speed)

    directionToVector = staticmethod(directionToVector)

    def getPossibleActions(config, walls):
        possible = []
        x, y = config.pos
        x_int, y_int = int(x + 0.5), int(y + 0.5)

        # In between grid points, all agents must continue straight
        if abs(x - x_int) + abs(y - y_int) > Actions.TOLERANCE:
            return [config.getDirection()]

        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_y = y_int + dy
            next_x = x_int + dx
            if not walls[next_x][next_y]:
                possible.append(dir)

        return possible

    getPossibleActions = staticmethod(getPossibleActions)

    def getLegalNeighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []
        for dir, vec in Actions._directionsAsList:
            dx, dy = vec
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.width:
                continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.height:
                continue
            if not walls[next_x][next_y]:
                neighbors.append((next_x, next_y))
        return neighbors

    getLegalNeighbors = staticmethod(getLegalNeighbors)

    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        return (x + dx, y + dy)

    getSuccessor = staticmethod(getSuccessor)


class GameStateData:
    """
    Stores the mutable data for a station mission.
    """

    def __init__(self, prevState=None):
        """
        Generates a new data packet by copying information from its predecessor.
        """
        self.legacyTargets = None
        self.agentStates = []
        self.layout = None
        self.cumulativeCost = 0
        self.completedLegacyCount = 0

        self.missionType = "legacy"
        self.diagnosticTerminal = None
        self.controlPosition = None
        self.modulePosition = None
        self.kitPosition = None
        self.pendingSystems = tuple()
        self.totalSystems = 0
        self.hasModule = False
        self.hasKit = False
        self.repairedCount = 0

        self.legacyTargetCompleted = None
        self.missionEvent = None
        self._agentMoved = None
        self._lose = False
        self._win = False

        if prevState is not None:
            self.legacyTargets = prevState.legacyTargets.shallowCopy()
            self.agentStates = self.copyAgentStates(prevState.agentStates)
            self.layout = prevState.layout
            self.cumulativeCost = prevState.cumulativeCost
            self.completedLegacyCount = prevState.completedLegacyCount
            self.missionType = prevState.missionType
            self.diagnosticTerminal = prevState.diagnosticTerminal
            self.controlPosition = prevState.controlPosition
            self.modulePosition = prevState.modulePosition
            self.kitPosition = prevState.kitPosition
            self.pendingSystems = prevState.pendingSystems
            self.totalSystems = prevState.totalSystems
            self.hasModule = prevState.hasModule
            self.hasKit = prevState.hasKit
            self.repairedCount = prevState.repairedCount
            self._lose = prevState._lose
            self._win = prevState._win

    def deepCopy(self):
        state = GameStateData(self)
        state.legacyTargets = self.legacyTargets.deepCopy()
        state.layout = self.layout.deepCopy()
        state._agentMoved = self._agentMoved
        state.legacyTargetCompleted = self.legacyTargetCompleted
        state.missionEvent = self.missionEvent
        state.cumulativeCost = self.cumulativeCost
        state.completedLegacyCount = self.completedLegacyCount
        state.pendingSystems = self.pendingSystems
        return state

    def copyAgentStates(self, agentStates):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """
        if other is None:
            return False
        if not self.agentStates == other.agentStates:
            return False
        if not self.legacyTargets == other.legacyTargets:
            return False
        if self.missionType != other.missionType:
            return False
        if self.hasModule != other.hasModule:
            return False
        if self.hasKit != other.hasKit:
            return False
        if self.pendingSystems != other.pendingSystems:
            return False
        return True

    def __hash__(self):
        """
        Allows states to be keys of dictionaries.
        """
        for i, state in enumerate(self.agentStates):
            try:
                int(hash(state))
            except TypeError as e:
                print(e)
                # hash(state)
        return int(
            (
                hash(tuple(self.agentStates))
                + 13 * hash(self.legacyTargets)
                + 17 * hash(self.missionType)
                + 19 * hash(self.hasModule)
                + 23 * hash(self.hasKit)
                + 29 * hash(self.pendingSystems)
            )
            % 1048575
        )

    def __str__(self):
        width, height = self.layout.width, self.layout.height
        map = Grid(width, height)
        if isinstance(self.legacyTargets, tuple):
            self.legacyTargets = reconstituteGrid(self.legacyTargets)
        for x in range(width):
            for y in range(height):
                legacyTargets, walls = self.legacyTargets, self.layout.walls
                map[x][y] = self._cellStr(legacyTargets[x][y], walls[x][y], x, y)

        for agentState in self.agentStates:
            if agentState is None:
                continue
            if agentState.configuration is None:
                continue
            x, y = [int(i) for i in nearestPoint(agentState.configuration.pos)]
            agent_dir = agentState.configuration.direction
            map[x][y] = self._agentStr(agent_dir)

        return (
            str(map)
            + ("\nCosto: %d\n" % self.cumulativeCost)
            + ("%s\n" % self.getMissionStatusText())
        )

    def _cellStr(self, hasLegacyTarget, hasWall, x=None, y=None):
        if hasLegacyTarget:
            return "S"
        elif hasWall:
            return "%"
        else:
            missionSymbol = self._missionSymbolAt((x, y))
            if missionSymbol is not None:
                return missionSymbol
            if x is not None and y is not None and hasattr(self.layout, "getTerrain"):
                t = self.layout.getTerrain(x, y)
                if t in ["~", "^", "*"]:
                    return t
        return " "

    def _missionSymbolAt(self, position):
        """
        Returns the visible mission symbol at a position, if any.
        """
        if self.missionType == "diagnostic":
            if position == self.diagnosticTerminal:
                return "D"
        elif self.missionType == "module":
            if position == self.controlPosition:
                return "C"
            if position == self.modulePosition and not self.hasModule:
                return "M"
        elif self.missionType == "systems":
            if position == self.controlPosition:
                return "C"
            if position == self.kitPosition and not self.hasKit:
                return "K"
            if position in self.pendingSystems:
                return "T"
        return None

    def _agentStr(self, dir):
        if dir == Directions.NORTH:
            return "^"
        if dir == Directions.SOUTH:
            return "v"
        if dir == Directions.WEST:
            return "<"
        if dir == Directions.EAST:
            return ">"
        if dir == Directions.STOP:
            return "<"

    def initialize(self, layout):
        """
        Creates an initial game state from a layout array.
        """
        self.legacyTargets = layout.legacyTargets.copy()
        self.layout = layout
        self.cumulativeCost = 0
        self.completedLegacyCount = 0
        self._lose = False
        self._win = False
        self.legacyTargetCompleted = None
        self.missionEvent = None
        self._initializeStationMission(layout)

        self.agentStates = []
        for pos in layout.agentPositions:
            self.agentStates.append(AgentState(Configuration(pos, Directions.STOP)))

    def _initializeStationMission(self, layout):
        """
        Detects the station mission represented by the layout symbols.
        """
        diagnosticPositions = layout.getSymbolPositions("D")
        modulePositions = layout.getSymbolPositions("M")
        kitPositions = layout.getSymbolPositions("K")
        controlPositions = layout.getSymbolPositions("C")
        systemPositions = layout.getSymbolPositions("T")

        self.diagnosticTerminal = None
        self.controlPosition = None
        self.modulePosition = None
        self.kitPosition = None
        self.pendingSystems = tuple()
        self.totalSystems = 0
        self.hasModule = False
        self.hasKit = False
        self.repairedCount = 0

        if len(diagnosticPositions) == 1:
            self.missionType = "diagnostic"
            self.diagnosticTerminal = diagnosticPositions[0]
        elif (
            len(kitPositions) == 1
            and len(controlPositions) == 1
            and len(systemPositions) > 0
        ):
            self.missionType = "systems"
            self.kitPosition = kitPositions[0]
            self.controlPosition = controlPositions[0]
            self.pendingSystems = tuple(sorted(systemPositions))
            self.totalSystems = len(self.pendingSystems)
        elif len(modulePositions) == 1 and len(controlPositions) == 1:
            self.missionType = "module"
            self.modulePosition = modulePositions[0]
            self.controlPosition = controlPositions[0]
        else:
            self.missionType = "legacy"

    def getObjectiveText(self):
        """
        Returns a short objective description for displays.
        """
        if self.missionType == "diagnostic":
            return "Alcanzar el terminal de diagnóstico D"
        if self.missionType == "module":
            return "Recoger M y entregarlo en C"
        if self.missionType == "systems":
            return "Recoger K, reparar todos los T y volver a C"
        return "Completar todos los objetivos heredados S"

    def getMissionStatusText(self):
        """
        Returns a compact mission status string.
        """
        if self.missionType == "diagnostic":
            status = "alcanzado" if self._win else "pendiente"
            return "Objetivo: terminal D %s" % status
        if self.missionType == "module":
            moduleStatus = "sí" if self.hasModule else "no"
            return "Objetivo: módulo=%s, terminar en C" % moduleStatus
        if self.missionType == "systems":
            kitStatus = "sí" if self.hasKit else "no"
            return "Objetivo: kit=%s, sistemas=%d/%d" % (
                kitStatus,
                self.repairedCount,
                self.totalSystems,
            )
        totalLegacyTargets = (
            self.layout.totalLegacyTargets if self.layout is not None else 0
        )
        return "Objetivo: heredados=%d/%d" % (
            self.completedLegacyCount,
            totalLegacyTargets,
        )


class Game:
    """
    The Game manages the control flow, soliciting actions from agents.
    """

    def __init__(
        self,
        agents,
        display,
        rules,
        startingIndex=0,
        muteAgents=False,
        catchExceptions=False,
    ):
        self.agentCrashed = False
        self.agents = agents
        self.display = display
        self.rules = rules
        self.startingIndex = startingIndex
        self.gameOver = False
        self.muteAgents = muteAgents
        self.catchExceptions = catchExceptions
        self.moveHistory = []
        self.totalAgentTimes = [0 for agent in agents]
        self.totalAgentTimeWarnings = [0 for agent in agents]
        self.agentTimeout = False
        import io

        self.agentOutput = [io.StringIO() for agent in agents]

    def getProgress(self):
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    def _agentCrash(self, quiet=False):
        "Helper method for handling agent crashes"
        if not quiet:
            traceback.print_exc()
        self.gameOver = True
        self.agentCrashed = True

    OLD_STDOUT = None
    OLD_STDERR = None

    def mute(self, agentIndex):
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR

        OLD_STDOUT = sys.stdout
        OLD_STDERR = sys.stderr
        sys.stdout = self.agentOutput[agentIndex]
        sys.stderr = self.agentOutput[agentIndex]

    def unmute(self):
        if not self.muteAgents:
            return
        global OLD_STDOUT, OLD_STDERR
        # Revert stdout/stderr to originals
        sys.stdout = OLD_STDOUT
        sys.stderr = OLD_STDERR

    def run(self):
        """
        Main control loop for game play.
        """
        self.display.initialize(self.state.data)
        time.sleep(0.5)  # Pause so user can locate the agent before it moves
        self.numMoves = 0

        # inform learning agents of the game start
        for i in range(len(self.agents)):
            agent = self.agents[i]
            if not agent:
                self.mute(i)
                print("Agent %d failed to load" % i, file=sys.stderr)
                self.unmute()
                self._agentCrash(quiet=True)
                return
            if "registerInitialState" in dir(agent):
                self.mute(i)
                if self.catchExceptions:
                    try:
                        start_time = time.time()
                        agent.registerInitialState(self.state.deepCopy())
                        time_taken = time.time() - start_time
                        self.totalAgentTimes[i] += time_taken
                    except Exception:
                        self._agentCrash(quiet=False)
                        self.unmute()
                        return
                else:
                    agent.registerInitialState(self.state.deepCopy())
                self.unmute()

        agentIndex = self.startingIndex
        numAgents = len(self.agents)

        while not self.gameOver:
            # Fetch the next agent
            agent = self.agents[agentIndex]
            move_time = 0
            # Generate an observation of the state
            if "observationFunction" in dir(agent):
                self.mute(agentIndex)
                if self.catchExceptions:
                    try:
                        start_time = time.time()
                        observation = agent.observationFunction(self.state.deepCopy())
                        move_time += time.time() - start_time
                        self.unmute()
                    except Exception:
                        self._agentCrash(quiet=False)
                        self.unmute()
                        return
                else:
                    observation = agent.observationFunction(self.state.deepCopy())
                self.unmute()
            else:
                observation = self.state.deepCopy()

            # Solicit an action
            action = None
            self.mute(agentIndex)
            if self.catchExceptions:
                try:
                    start_time = time.time()
                    action = agent.getAction(observation)
                    move_time += time.time() - start_time
                    self.totalAgentTimes[agentIndex] += move_time
                    self.unmute()
                except Exception:
                    self._agentCrash()
                    self.unmute()
                    return
            else:
                action = agent.getAction(observation)
            self.unmute()

            # Execute the action
            self.moveHistory.append((agentIndex, action))
            if self.catchExceptions:
                try:
                    self.state = self.state.generateSuccessor(action)
                except Exception:
                    self.mute(agentIndex)
                    self._agentCrash()
                    self.unmute()
                    return
            else:
                self.state = self.state.generateSuccessor(action)

            # Change the display
            self.display.update(self.state.data)
            ###idx = agentIndex - agentIndex % 2 + 1
            ###self.display.update( self.state.makeObservation(idx).data )

            # Allow for game specific conditions (winning, losing, etc.)
            self.rules.process(self.state, self)
            # Track progress
            if agentIndex == numAgents + 1:
                self.numMoves += 1
            # Next agent
            agentIndex = (agentIndex + 1) % numAgents

        # inform a learning agent of the game result
        for agentIndex, agent in enumerate(self.agents):
            if "final" in dir(agent):
                try:
                    self.mute(agentIndex)
                    agent.final(self.state)
                    self.unmute()
                except Exception as data:
                    if not self.catchExceptions:
                        raise data
                    self._agentCrash()
                    self.unmute()
                    return
        self.display.finish()
