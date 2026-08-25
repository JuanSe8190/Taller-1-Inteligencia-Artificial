from world.game import Grid
import os


class StationLayout:
    """
    A StationLayout manages the static information about the station map.
    """

    def __init__(self, layoutText):
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.walls = Grid(self.width, self.height, False)
        self.legacyTargets = Grid(self.width, self.height, False)

        self.agentPositions = []
        self.terrain = {}
        self.missionSymbols = {}
        self.processLayoutText(layoutText)
        self.layoutText = layoutText
        self.totalLegacyTargets = len(self.legacyTargets.asList())

    def isWall(self, pos):
        """
        Check if position is a wall.
        """
        x, col = pos
        return self.walls[x][col]

    def getTerrain(self, x, y):
        """
        Get the terrain character at position (x, y).
        Returns the terrain character or '.' for normal floor.
        """
        return self.terrain.get((x, y), ".")

    def getTerrainCost(self, x, y):
        """
        Get the movement cost for terrain at position (x, y).

        Terrain costs:
        - Normal floor (' ' or '.'): 1
        - Low gravity zone ('~'): 2
        - Damaged corridor ('^'): 3
        - High radiation zone ('*'): 5
        """
        terrain_char = self.getTerrain(x, y)
        TERRAIN_COSTS = {
            ".": 1,  # Normal floor
            " ": 1,  # Empty space
            "~": 2,  # Low gravity zone
            "^": 3,  # Damaged corridor
            "*": 5,  # High radiation zone
        }
        return TERRAIN_COSTS.get(terrain_char, 1)

    def getSymbolPositions(self, symbol):
        """
        Get every position where a mission symbol appears.
        """
        return self.missionSymbols.get(symbol, [])[:]

    def getSymbolPosition(self, symbol):
        """
        Get the single position for a mission symbol.
        """
        positions = self.getSymbolPositions(symbol)

        if len(positions) != 1:
            raise Exception(
                "Expected exactly one '%s' symbol in the layout, found %d"
                % (symbol, len(positions))
            )

        return positions[0]

    def __str__(self):
        return "\n".join(self.layoutText)

    def deepCopy(self):
        return StationLayout(self.layoutText[:])

    def processLayoutText(self, layoutText):
        """
        Coordinates are flipped from the input format to the (x,y) convention here

        The shape of the station. Each character represents a different type of object:
         % - Wall/Obstacle (impassable)
         R - Robot (starting position)
         D - Diagnostic terminal
         C - Control center
         M - Energy module
         K - Repair kit
         T - Damaged system
         . - Normal floor (movement cost 1)
         ~ - Low gravity zone (movement cost 2)
         ^ - Damaged corridor (movement cost 3)
         * - High radiation zone (movement cost 5)

        Other characters are treated as normal floor (cost 1).
        """
        maxY = self.height - 1
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutText[maxY - y][x]
                self.processLayoutChar(x, y, layoutChar)
        self.agentPositions.sort()

    def processLayoutChar(self, x, y, layoutChar):
        """
        Process a single layout character and update the appropriate data structure.
        """
        # Walls
        if layoutChar == "%":
            self.walls[x][y] = True

        # Legacy target symbol from older layouts
        elif layoutChar == "S":
            self.legacyTargets[x][y] = True

        # Robot starting position
        elif layoutChar == "R":
            self.agentPositions.append((x, y))

        # Terrain types for variable movement costs
        elif layoutChar in ["~", "^", "*"]:
            self.terrain[(x, y)] = layoutChar

        # Mission symbols for the station maintenance problems
        elif layoutChar in ["D", "C", "M", "K", "T"]:
            self.missionSymbols.setdefault(layoutChar, []).append((x, y))

        # All other characters (including ' ') are treated as normal floor
        # They don't create walls, mission symbols, or special terrain


def getLayout(name):
    """
    Load a layout file by name.

    Searches recursively inside the layouts/ directory for a matching .lay file.
    """
    filename = name if name.endswith(".lay") else name + ".lay"
    for root, _dirs, files in os.walk("layouts"):
        if filename in files:
            return tryToLoad(os.path.join(root, filename))
    return None


def tryToLoad(fullname):
    """
    Attempt to load a layout from a file.
    Returns None if file doesn't exist.
    """
    if not os.path.exists(fullname):
        return None
    f = open(fullname)
    try:
        return StationLayout([line.strip() for line in f])
    finally:
        f.close()
