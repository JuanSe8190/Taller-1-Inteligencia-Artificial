from view.graphics_utils import (
    refresh,
    formatColor,
    text,
    line,
    polygon,
    square,
    circle,
    remove_from_screen,
    begin_graphics,
    begin_graphics_scrollable,
    end_graphics,
    sleep,
    keys_pressed,
    keys_waiting,
    changeText,
    edit,
)
from world.game import Directions

# ========================================
# CHANGES TO LAYOUT
# ========================================

DEFAULT_GRID_SIZE = 30.0
INFO_PANE_HEIGHT = 74
INFO_PANE_PADDING = 12
MAX_WINDOW_WIDTH = 1400
MAX_WINDOW_HEIGHT = 900
VIEWPORT_MAX_WIDTH = 1280
VIEWPORT_MAX_HEIGHT = 720

# Environment (station interior)
BACKGROUND_COLOR = formatColor(0.92, 0.93, 0.94)  # Light station floor
GRID_LINE_COLOR = formatColor(0.82, 0.84, 0.86)  # Subtle panel seams

# Walls
WALL_FILL = formatColor(0.35, 0.36, 0.38)  # Dark station bulkhead
WALL_OUTLINE = formatColor(0.16, 0.17, 0.18)  # Almost black outline
WALL_HIGHLIGHT = formatColor(0.52, 0.53, 0.55)
WALL_SHADOW = formatColor(0.24, 0.25, 0.27)
WALL_RIVET = formatColor(0.12, 0.13, 0.14)

# Terrain (station traversal zones)
LOW_GRAVITY_BASE = formatColor(0.38, 0.50, 0.86)  # Low gravity corridor
LOW_GRAVITY_GLOW = formatColor(0.70, 0.82, 1.0)
LOW_GRAVITY_DOT = formatColor(0.86, 0.92, 1.0)

DAMAGED_CORRIDOR_BASE = formatColor(0.48, 0.45, 0.40)  # Damaged corridor
DAMAGED_CORRIDOR_PANEL = formatColor(0.35, 0.34, 0.33)
DAMAGED_CORRIDOR_STRIPE = formatColor(0.95, 0.72, 0.18)
DAMAGED_CORRIDOR_CRACK = formatColor(0.12, 0.12, 0.12)

RADIATION_BASE = formatColor(0.55, 0.26, 0.74)  # High radiation zone
RADIATION_GLOW = formatColor(0.86, 0.56, 1.0)
RADIATION_CORE = formatColor(1.0, 0.76, 0.18)
RADIATION_MARK = formatColor(0.16, 0.05, 0.20)
COST_LABEL_FILL = formatColor(0.03, 0.03, 0.03)
COST_LABEL_TEXT = formatColor(1.0, 1.0, 1.0)

# Mission Elements
TERMINAL_FILL = formatColor(0.20, 0.45, 0.85)  # Diagnostic terminal
TERMINAL_SCREEN = formatColor(0.05, 0.18, 0.32)
TERMINAL_GLOW = formatColor(0.45, 0.85, 1.0)
CONTROL_FILL = formatColor(0.35, 0.30, 0.70)  # Control center
CONTROL_SCREEN = formatColor(0.08, 0.10, 0.25)
CONTROL_LIGHT = formatColor(0.95, 0.80, 0.20)
MODULE_FILL = formatColor(0.95, 0.62, 0.18)  # Energy module
MODULE_CASE = formatColor(0.55, 0.38, 0.12)
MODULE_ENERGY = formatColor(1.0, 0.92, 0.20)
KIT_FILL = formatColor(0.18, 0.65, 0.45)  # Repair kit
KIT_HANDLE = formatColor(0.08, 0.36, 0.25)
KIT_CROSS = formatColor(0.92, 1.0, 0.95)
SYSTEM_FILL = formatColor(0.90, 0.32, 0.22)  # Damaged system
SYSTEM_PANEL = formatColor(0.34, 0.08, 0.08)
SYSTEM_CRACK = formatColor(0.06, 0.06, 0.06)
SYSTEM_WARNING = formatColor(1.0, 0.88, 0.20)
MISSION_OUTLINE = formatColor(0.10, 0.10, 0.10)
MISSION_TEXT = formatColor(1.0, 1.0, 1.0)
COMPLETED_FILL = formatColor(0.25, 0.75, 0.35)
COMPLETED_OUTLINE = formatColor(0.12, 0.45, 0.18)
COMPLETED_TEXT = formatColor(0.1, 0.1, 0.1)

# Robot (station maintenance unit)
ROBOT_BODY = formatColor(0.25, 0.35, 0.50)  # Navy blue body
ROBOT_ACCENT = formatColor(0.35, 0.55, 0.75)  # Light blue accents
ROBOT_SENSOR = formatColor(0.0, 0.85, 0.30)  # Bright green sensors
ROBOT_OUTLINE = formatColor(0.1, 0.1, 0.1)  # Dark outline
ROBOT_SHADOW = formatColor(0.70, 0.72, 0.74)
ROBOT_TREAD = formatColor(0.08, 0.09, 0.10)
ROBOT_VISOR = formatColor(0.50, 0.85, 1.0)
ROBOT_LIGHT = formatColor(0.05, 1.0, 0.55)

# Info Pane
COST_COLOR = formatColor(0.2, 0.2, 0.2)  # Dark gray text
TITLE_COLOR = formatColor(0.3, 0.3, 0.3)  # Medium gray
STATUS_COLOR = formatColor(0.20, 0.35, 0.55)


# ========================================
# INFO PANE
# ========================================


class InfoPane:
    def __init__(self, state, gridSize):
        self.gridSize = gridSize
        layout = state.layout
        self.left = 0.5 * gridSize
        self.width = layout.width * gridSize
        self.base = (layout.height + 1) * gridSize

        # Responsive font sizing based on width
        if self.width < 300:
            self.fontSize = 12
            self.titleSize = 10
        elif self.width < 500:
            self.fontSize = 14
            self.titleSize = 11
        else:
            self.fontSize = 16
            self.titleSize = 12

        self.drawPane(state)

    def toScreen(self, x, y):
        return (self.left + x, self.base + y)

    def drawPane(self, state):
        # Title - centered, with vertical padding
        titleX = self.width // 2
        self.titleText = text(
            self.toScreen(titleX, 4),
            TITLE_COLOR,
            "MANTENIMIENTO DE ESTACIÓN",
            "Arial",
            self.titleSize,
            "bold",
            anchor="n",  # North anchor (centered at top)
        )

        # Cost - left side with padding
        self.costText = text(
            self.toScreen(INFO_PANE_PADDING, 24),
            COST_COLOR,
            "COSTO: 0",
            "Arial",
            self.fontSize,
            "bold",
            anchor="nw",
        )

        # Objective - right side with padding
        self.objectiveText = text(
            self.toScreen(self.width - INFO_PANE_PADDING, 24),
            STATUS_COLOR,
            self._shortObjective(state),
            "Arial",
            self.fontSize,
            "bold",
            anchor="ne",  # Northeast anchor (right-aligned)
        )

        # Mission status - bottom row
        self.statusText = text(
            self.toScreen(INFO_PANE_PADDING, 50),
            STATUS_COLOR,
            state.getMissionStatusText(),
            "Arial",
            self.fontSize,
            "bold",
            anchor="nw",
        )

    def updateCost(self, cost):
        changeText(self.costText, f"COSTO: {cost}")

    def updateMissionStatus(self, state):
        changeText(self.objectiveText, self._shortObjective(state))
        changeText(self.statusText, state.getMissionStatusText())

    def _shortObjective(self, state):
        if state.missionType == "diagnostic":
            return "META: D"
        if state.missionType == "module":
            return "META: M -> C"
        if state.missionType == "systems":
            return "META: K -> T -> C"
        return "META: MISIÓN"


# ========================================
# MAIN GRAPHICS CLASS
# ========================================


class StationGraphics:
    def __init__(self, zoom=1.0, frameTime=0.0, capture=False):
        self.zoom = zoom
        self.gridSize = DEFAULT_GRID_SIZE * zoom
        self.frameTime = frameTime
        self.capture = capture
        self._step_mode_message_shown = False

        self.gridLines = []
        self.terrainTiles = []
        self.terrainLabels = []
        self.legacyTargetImages = None
        self.missionElementImages = {}
        self.agentImages = []
        self.totalLegacyTargets = 0
        self._stateHistory = []
        self._historyIndex = 0

    def initialize(self, state, isBlue=False):
        """
        Initialize display with mission state.
        """
        self.layout = state.layout
        self.width = self.layout.width
        self.height = self.layout.height
        self.totalLegacyTargets = self.layout.totalLegacyTargets

        # Use scroll when content exceeds viewport safe size; otherwise scale down so it fits
        screen_width = 2 * self.gridSize + (self.width - 1) * self.gridSize
        screen_height = 2 * self.gridSize + (self.height - 1) * self.gridSize + INFO_PANE_HEIGHT
        self._use_scroll = (
            screen_width > VIEWPORT_MAX_WIDTH or screen_height > VIEWPORT_MAX_HEIGHT
        )
        if self._use_scroll:
            # Keep full resolution; viewport will have scrollbars
            self._content_width = int(screen_width)
            self._content_height = int(screen_height)
        else:
            # Scale down to fit
            if screen_width > MAX_WINDOW_WIDTH or screen_height > MAX_WINDOW_HEIGHT:
                scale = min(MAX_WINDOW_WIDTH / screen_width, MAX_WINDOW_HEIGHT / screen_height)
                self.gridSize *= scale
                screen_width = 2 * self.gridSize + (self.width - 1) * self.gridSize
                screen_height = 2 * self.gridSize + (self.height - 1) * self.gridSize + INFO_PANE_HEIGHT
            self._content_width = int(screen_width)
            self._content_height = int(screen_height)

        self._make_window()
        self.infoPane = InfoPane(state, self.gridSize)

        self._drawStatic(state)
        self._drawAgents(state)
        self.previousState = state
        self._stateHistory = [state]
        self._historyIndex = 0

    def finish(self):
        end_graphics()

    # ========================================
    # WINDOW SETUP
    # ========================================

    def _make_window(self):
        """
        Create window with professional styling. Uses scroll when content is large.
        """
        if getattr(self, "_use_scroll", False):
            viewport_w = min(VIEWPORT_MAX_WIDTH, self._content_width)
            viewport_h = min(VIEWPORT_MAX_HEIGHT, self._content_height)
            begin_graphics_scrollable(
                viewport_w,
                viewport_h,
                self._content_width,
                self._content_height,
                BACKGROUND_COLOR,
                "Control de Misión de la Estación",
            )
        else:
            begin_graphics(
                self._content_width,
                self._content_height,
                BACKGROUND_COLOR,
                "Control de Misión de la Estación",
            )

    def to_screen(self, point):
        """
        Convert grid coordinates to screen coordinates.
        """
        x, y = point
        x = (x + 1) * self.gridSize
        y = (self.height - y) * self.gridSize
        return (x, y)

    def _rectangle(
        self,
        center,
        halfWidth,
        halfHeight,
        outlineColor,
        fillColor=None,
        filled=1,
        width=1,
    ):
        """
        Draw an axis-aligned rectangle centered at center.
        """
        x, y = center
        coords = [
            (x - halfWidth, y - halfHeight),
            (x + halfWidth, y - halfHeight),
            (x + halfWidth, y + halfHeight),
            (x - halfWidth, y + halfHeight),
        ]
        return polygon(
            coords,
            outlineColor,
            fillColor if fillColor is not None else outlineColor,
            filled=filled,
            smoothed=0,
            width=width,
        )

    def _scaledText(self, center, color, contents, scale=0.38, style="bold"):
        """
        Draw text that follows the current grid size.
        """
        fontSize = max(8, int(scale * self.gridSize))
        return text(center, color, contents, "Arial", fontSize, style, anchor="center")

    def _costLabel(self, screen, contents):
        """
        Draw a terrain cost label in the lower-right corner of a cell.
        """
        g = self.gridSize
        labelPosition = (screen[0] + 0.30 * g, screen[1] + 0.28 * g)
        badge = circle(labelPosition, 0.17 * g, COST_LABEL_FILL, COST_LABEL_FILL)
        label = self._scaledText(
            labelPosition,
            COST_LABEL_TEXT,
            contents,
            scale=0.34,
        )
        return [badge, label]

    # ========================================
    # STATIC ELEMENTS
    # ========================================

    def _drawStatic(self, state):
        """
        Draw all static elements (background, walls, terrain, mission objects).
        """
        # 1. Background grid
        self._drawBackgroundGrid()

        # 2. Terrain
        self._drawTerrain(state)

        # 3. Walls
        self._drawWalls(state.layout.walls)

        # 4. Mission objects
        if getattr(state, "missionType", "legacy") == "legacy":
            self.legacyTargetImages = self._drawLegacyTargets(state.legacyTargets)
        else:
            self.missionElementImages = self._drawMissionElements(state)

        refresh()

    def _drawBackgroundGrid(self):
        """
        Draw subtle grid lines for spatial reference.
        """
        left = 0.5 * self.gridSize
        right = (self.width + 0.5) * self.gridSize
        top = 0.5 * self.gridSize
        bottom = (self.height + 0.5) * self.gridSize

        for x in range(self.width + 1):
            x_screen = (x + 0.5) * self.gridSize
            line_obj = line(
                (x_screen, top),
                (x_screen, bottom),
                GRID_LINE_COLOR,
                width=1,
            )
            self.gridLines.append(line_obj)

        for y in range(self.height + 1):
            y_screen = (y + 0.5) * self.gridSize
            line_obj = line(
                (left, y_screen),
                (right, y_screen),
                GRID_LINE_COLOR,
                width=1,
            )
            self.gridLines.append(line_obj)

    def _drawWalls(self, wallMatrix):
        """
        Draw walls as station bulkhead panels.
        """
        for x in range(wallMatrix.width):
            for y in range(wallMatrix.height):
                if not wallMatrix[x][y]:
                    continue

                screen = self.to_screen((x, y))
                g = self.gridSize

                # Main wall block
                square(screen, 0.48 * g, color=WALL_FILL, filled=1)

                # Panel edges for depth
                square(screen, 0.48 * g, color=WALL_OUTLINE, filled=0, behind=0)
                line(
                    (screen[0] - 0.38 * g, screen[1] - 0.30 * g),
                    (screen[0] + 0.38 * g, screen[1] - 0.30 * g),
                    WALL_HIGHLIGHT,
                    width=1,
                )
                line(
                    (screen[0] - 0.34 * g, screen[1] + 0.30 * g),
                    (screen[0] + 0.34 * g, screen[1] + 0.30 * g),
                    WALL_SHADOW,
                    width=1,
                )

                # Small rivet marks
                circle(
                    (screen[0] - 0.26 * g, screen[1] - 0.20 * g),
                    0.025 * g,
                    WALL_RIVET,
                    WALL_RIVET,
                )
                circle(
                    (screen[0] + 0.26 * g, screen[1] + 0.20 * g),
                    0.025 * g,
                    WALL_RIVET,
                    WALL_RIVET,
                )

    def _drawTerrain(self, state):
        """
        Draw terrain with realistic styling.
        """
        # Clear old terrain
        for obj in self.terrainTiles + self.terrainLabels:
            remove_from_screen(obj)
        self.terrainTiles = []
        self.terrainLabels = []

        layout = state.layout
        walls = layout.walls

        for x in range(walls.width):
            for y in range(walls.height):
                if walls[x][y]:
                    continue

                terrain_char = (
                    layout.getTerrain(x, y) if hasattr(layout, "getTerrain") else "."
                )

                if terrain_char == "~":
                    self._drawLowGravityZone(x, y)
                elif terrain_char == "^":
                    self._drawDamagedCorridor(x, y)
                elif terrain_char == "*":
                    self._drawRadiationZone(x, y)

    def _drawLowGravityZone(self, x, y):
        """
        Draw a low-gravity corridor zone.
        """
        screen = self.to_screen((x, y))
        g = self.gridSize

        # Base low-gravity field
        tile = square(screen, 0.5 * g, color=LOW_GRAVITY_BASE, filled=1)
        self.terrainTiles.append(tile)

        # Floating field lines
        for offset in [-0.22, 0.00, 0.22]:
            self.terrainTiles.append(
                line(
                    (screen[0] - 0.34 * g, screen[1] + offset * g),
                    (screen[0] + 0.34 * g, screen[1] + offset * g),
                    LOW_GRAVITY_GLOW,
                    width=2,
                )
            )
        for px, py in [(-0.24, -0.13), (0.23, 0.12), (-0.05, 0.24)]:
            self.terrainTiles.append(
                circle(
                    (screen[0] + px * g, screen[1] + py * g),
                    0.045 * g,
                    LOW_GRAVITY_DOT,
                    LOW_GRAVITY_DOT,
                )
            )
        self.terrainTiles.append(
            polygon(
                [
                    (screen[0], screen[1] - 0.27 * g),
                    (screen[0] - 0.08 * g, screen[1] - 0.14 * g),
                    (screen[0] + 0.08 * g, screen[1] - 0.14 * g),
                ],
                LOW_GRAVITY_DOT,
                LOW_GRAVITY_DOT,
                filled=1,
                smoothed=0,
            )
        )

        # Cost label
        self.terrainLabels.extend(self._costLabel(screen, "2"))

    def _drawDamagedCorridor(self, x, y):
        """
        Draw a damaged corridor with unstable panels and warning marks.
        """
        screen = self.to_screen((x, y))
        g = self.gridSize

        # Base damaged floor panel
        tile = square(screen, 0.5 * g, color=DAMAGED_CORRIDOR_BASE, filled=1)
        self.terrainTiles.append(tile)

        # Loose panels
        self.terrainTiles.append(
            self._rectangle(
                (screen[0] - 0.16 * g, screen[1] - 0.12 * g),
                0.14 * g,
                0.10 * g,
                DAMAGED_CORRIDOR_PANEL,
                DAMAGED_CORRIDOR_PANEL,
            )
        )
        self.terrainTiles.append(
            self._rectangle(
                (screen[0] + 0.17 * g, screen[1] + 0.11 * g),
                0.13 * g,
                0.10 * g,
                DAMAGED_CORRIDOR_PANEL,
                DAMAGED_CORRIDOR_PANEL,
            )
        )

        # Warning diagonal stripes
        for offset in [-0.28, 0.02, 0.32]:
            self.terrainTiles.append(
                line(
                    (screen[0] + (offset - 0.18) * g, screen[1] + 0.34 * g),
                    (screen[0] + (offset + 0.12) * g, screen[1] + 0.04 * g),
                    DAMAGED_CORRIDOR_STRIPE,
                    width=2,
                )
            )

        # Cost label
        self.terrainLabels.extend(self._costLabel(screen, "3"))

    def _drawRadiationZone(self, x, y):
        """
        Draw a high-radiation or high-energy corridor zone.
        """
        screen = self.to_screen((x, y))
        g = self.gridSize

        # Radiation field background
        glow = square(screen, 0.5 * g, color=RADIATION_GLOW, filled=1)
        self.terrainTiles.append(glow)

        # Inner radiation core
        core = circle(screen, 0.33 * g, RADIATION_BASE, RADIATION_BASE)
        self.terrainTiles.append(core)

        # Radiation symbol: center plus three warning lobes
        center = circle(
            screen,
            0.055 * g,
            RADIATION_CORE,
            RADIATION_CORE,
        )
        self.terrainTiles.append(center)
        for angle_points in [
            [
                (screen[0], screen[1] - 0.27 * g),
                (screen[0] - 0.08 * g, screen[1] - 0.09 * g),
                (screen[0] + 0.08 * g, screen[1] - 0.09 * g),
            ],
            [
                (screen[0] - 0.25 * g, screen[1] + 0.16 * g),
                (screen[0] - 0.04 * g, screen[1] + 0.07 * g),
                (screen[0] - 0.13 * g, screen[1] - 0.03 * g),
            ],
            [
                (screen[0] + 0.25 * g, screen[1] + 0.16 * g),
                (screen[0] + 0.04 * g, screen[1] + 0.07 * g),
                (screen[0] + 0.13 * g, screen[1] - 0.03 * g),
            ],
        ]:
            self.terrainTiles.append(
                polygon(
                    angle_points,
                    RADIATION_CORE,
                    RADIATION_CORE,
                    filled=1,
                    smoothed=0,
                )
            )
        # Cost label
        self.terrainLabels.extend(self._costLabel(screen, "5"))

    def _drawLegacyTargets(self, legacyTargetsMatrix):
        """
        Draw target markers for older S-based layouts.
        """
        images = []
        for x, col in enumerate(legacyTargetsMatrix):
            rowImgs = []
            images.append(rowImgs)
            for y, hasTarget in enumerate(col):
                if hasTarget:
                    screen = self.to_screen((x, y))

                    # Outer glow for attention
                    glow = circle(
                        screen, 0.32 * self.gridSize, MISSION_OUTLINE, MISSION_OUTLINE
                    )

                    # Inner bright circle
                    inner = circle(
                        screen, 0.26 * self.gridSize, SYSTEM_FILL, SYSTEM_FILL
                    )

                    # "S" text
                    label = text(screen, MISSION_TEXT, "S", "Arial", 11, "bold")

                    rowImgs.append([glow, inner, label])
                else:
                    rowImgs.append(None)
        return images

    def _drawMissionElements(self, state):
        """
        Draw station mission symbols.
        """
        images = {}
        layout = state.layout

        for position in layout.getSymbolPositions("D"):
            images[position] = self._drawMissionMarker(position, "D")
        for position in layout.getSymbolPositions("C"):
            images[position] = self._drawMissionMarker(position, "C")
        for position in layout.getSymbolPositions("M"):
            images[position] = self._drawMissionMarker(position, "M")
        for position in layout.getSymbolPositions("K"):
            images[position] = self._drawMissionMarker(position, "K")
        for position in layout.getSymbolPositions("T"):
            images[position] = self._drawMissionMarker(position, "T")

        return images

    def _drawMissionMarker(self, position, symbol):
        """
        Draw one mission marker at a grid position.
        """
        if symbol == "D":
            return self._drawDiagnosticTerminal(position)
        if symbol == "C":
            return self._drawControlCenter(position)
        if symbol == "M":
            return self._drawEnergyModule(position)
        if symbol == "K":
            return self._drawRepairKit(position)
        if symbol == "T":
            return self._drawDamagedSystem(position)

        return self._drawGenericMissionMarker(position, symbol)

    def _drawGenericMissionMarker(self, position, symbol):
        """
        Draw a fallback mission marker.
        """
        screen = self.to_screen(position)
        fillColor = self._missionFill(symbol)

        outer = circle(screen, 0.34 * self.gridSize, MISSION_OUTLINE, MISSION_OUTLINE)
        inner = square(screen, 0.26 * self.gridSize, color=fillColor, filled=1)
        label = self._scaledText(screen, MISSION_TEXT, symbol)

        return self._missionImage(symbol, outer, inner, label, [])

    def _missionImage(self, symbol, outer, inner, label, details):
        """
        Packs mission marker drawing ids for later updates.
        """
        return {
            "symbol": symbol,
            "outer": outer,
            "inner": inner,
            "innerOutline": MISSION_OUTLINE,
            "label": label,
            "details": details,
        }

    def _drawDiagnosticTerminal(self, position):
        """
        Draw a diagnostic terminal with screen and signal lines.
        """
        screen = self.to_screen(position)
        g = self.gridSize
        details = []

        outer = circle(screen, 0.36 * g, MISSION_OUTLINE, MISSION_OUTLINE)
        body = self._rectangle(screen, 0.30 * g, 0.30 * g, MISSION_OUTLINE, TERMINAL_FILL)
        display = self._rectangle(
            (screen[0], screen[1] - 0.08 * g),
            0.22 * g,
            0.12 * g,
            TERMINAL_SCREEN,
            TERMINAL_SCREEN,
        )
        details.append(display)
        details.append(
            line(
                (screen[0] - 0.14 * g, screen[1] - 0.08 * g),
                (screen[0] + 0.14 * g, screen[1] - 0.08 * g),
                TERMINAL_GLOW,
                width=2,
            )
        )
        details.append(
            line(
                (screen[0] - 0.08 * g, screen[1] - 0.01 * g),
                (screen[0] + 0.08 * g, screen[1] - 0.01 * g),
                TERMINAL_GLOW,
                width=2,
            )
        )
        details.append(
            line(
                (screen[0] - 0.18 * g, screen[1] + 0.17 * g),
                (screen[0] + 0.18 * g, screen[1] + 0.17 * g),
                MISSION_OUTLINE,
                width=2,
            )
        )
        label = self._scaledText(
            (screen[0], screen[1] + 0.18 * g),
            MISSION_TEXT,
            "D",
            scale=0.30,
        )

        return self._missionImage("D", outer, body, label, details)

    def _drawControlCenter(self, position):
        """
        Draw a control center console with display and status lights.
        """
        screen = self.to_screen(position)
        g = self.gridSize
        details = []

        outer = circle(screen, 0.38 * g, MISSION_OUTLINE, MISSION_OUTLINE)
        console = self._rectangle(screen, 0.32 * g, 0.28 * g, MISSION_OUTLINE, CONTROL_FILL)
        display = self._rectangle(
            (screen[0], screen[1] - 0.08 * g),
            0.24 * g,
            0.10 * g,
            CONTROL_SCREEN,
            CONTROL_SCREEN,
        )
        details.append(display)
        for offset, color in [
            (-0.14 * g, COMPLETED_FILL),
            (0, CONTROL_LIGHT),
            (0.14 * g, SYSTEM_FILL),
        ]:
            details.append(
                circle(
                    (screen[0] + offset, screen[1] + 0.10 * g),
                    0.035 * g,
                    color,
                    color,
                )
            )
        details.append(
            line(
                (screen[0] - 0.18 * g, screen[1] - 0.08 * g),
                (screen[0] + 0.18 * g, screen[1] - 0.08 * g),
                TERMINAL_GLOW,
                width=1,
            )
        )
        label = self._scaledText(
            (screen[0], screen[1] + 0.23 * g),
            MISSION_TEXT,
            "C",
            scale=0.26,
        )

        return self._missionImage("C", outer, console, label, details)

    def _drawEnergyModule(self, position):
        """
        Draw an energy module as a battery cell.
        """
        screen = self.to_screen(position)
        g = self.gridSize
        details = []

        outer = circle(screen, 0.36 * g, MISSION_OUTLINE, MISSION_OUTLINE)
        case = self._rectangle(screen, 0.25 * g, 0.32 * g, MISSION_OUTLINE, MODULE_FILL)
        details.append(
            self._rectangle(
                (screen[0], screen[1] - 0.38 * g),
                0.12 * g,
                0.04 * g,
                MODULE_CASE,
                MODULE_CASE,
            )
        )
        details.append(
            self._rectangle(
                (screen[0], screen[1] - 0.17 * g),
                0.16 * g,
                0.035 * g,
                MODULE_ENERGY,
                MODULE_ENERGY,
            )
        )
        details.append(
            self._rectangle(
                (screen[0], screen[1] - 0.04 * g),
                0.16 * g,
                0.035 * g,
                MODULE_ENERGY,
                MODULE_ENERGY,
            )
        )
        details.append(
            self._rectangle(
                (screen[0], screen[1] + 0.09 * g),
                0.16 * g,
                0.035 * g,
                MODULE_ENERGY,
                MODULE_ENERGY,
            )
        )
        label = self._scaledText(
            (screen[0], screen[1] + 0.24 * g),
            MISSION_TEXT,
            "M",
            scale=0.24,
        )

        return self._missionImage("M", outer, case, label, details)

    def _drawRepairKit(self, position):
        """
        Draw a repair kit as a compact tool case.
        """
        screen = self.to_screen(position)
        g = self.gridSize
        details = []

        outer = circle(screen, 0.36 * g, MISSION_OUTLINE, MISSION_OUTLINE)
        box = self._rectangle(
            (screen[0], screen[1] + 0.04 * g),
            0.31 * g,
            0.22 * g,
            MISSION_OUTLINE,
            KIT_FILL,
        )
        details.append(
            self._rectangle(
                (screen[0], screen[1] - 0.18 * g),
                0.17 * g,
                0.08 * g,
                KIT_HANDLE,
                KIT_FILL,
                filled=0,
                width=2,
            )
        )
        details.append(
            line(
                (screen[0] - 0.16 * g, screen[1] + 0.04 * g),
                (screen[0] + 0.16 * g, screen[1] + 0.04 * g),
                KIT_HANDLE,
                width=2,
            )
        )
        details.append(
            line(
                (screen[0] - 0.10 * g, screen[1] + 0.04 * g),
                (screen[0] + 0.10 * g, screen[1] + 0.04 * g),
                KIT_CROSS,
                width=3,
            )
        )
        details.append(
            line(
                (screen[0], screen[1] - 0.06 * g),
                (screen[0], screen[1] + 0.14 * g),
                KIT_CROSS,
                width=3,
            )
        )
        label = self._scaledText(
            (screen[0], screen[1] + 0.25 * g),
            MISSION_TEXT,
            "K",
            scale=0.22,
        )

        return self._missionImage("K", outer, box, label, details)

    def _drawDamagedSystem(self, position):
        """
        Draw a damaged system as a cracked warning panel.
        """
        screen = self.to_screen(position)
        g = self.gridSize
        details = []

        outer = circle(screen, 0.37 * g, MISSION_OUTLINE, MISSION_OUTLINE)
        panel = self._rectangle(screen, 0.30 * g, 0.28 * g, MISSION_OUTLINE, SYSTEM_FILL)
        warning = polygon(
            [
                (screen[0], screen[1] - 0.23 * g),
                (screen[0] - 0.13 * g, screen[1] + 0.02 * g),
                (screen[0] + 0.13 * g, screen[1] + 0.02 * g),
            ],
            SYSTEM_WARNING,
            SYSTEM_WARNING,
            filled=1,
            smoothed=0,
        )
        details.append(warning)
        details.append(
            self._scaledText(
                (screen[0], screen[1] - 0.07 * g),
                SYSTEM_PANEL,
                "!",
                scale=0.30,
            )
        )
        details.append(
            line(
                (screen[0] - 0.18 * g, screen[1] + 0.10 * g),
                (screen[0] - 0.02 * g, screen[1] + 0.02 * g),
                SYSTEM_CRACK,
                width=2,
            )
        )
        details.append(
            line(
                (screen[0] - 0.02 * g, screen[1] + 0.02 * g),
                (screen[0] + 0.14 * g, screen[1] + 0.16 * g),
                SYSTEM_CRACK,
                width=2,
            )
        )
        label = self._scaledText(
            (screen[0], screen[1] + 0.24 * g),
            MISSION_TEXT,
            "T",
            scale=0.22,
        )

        return self._missionImage("T", outer, panel, label, details)

    def _missionFill(self, symbol):
        """
        Returns the drawing color for a mission symbol.
        """
        colors = {
            "D": TERMINAL_FILL,
            "C": CONTROL_FILL,
            "M": MODULE_FILL,
            "K": KIT_FILL,
            "T": SYSTEM_FILL,
        }
        return colors.get(symbol, CONTROL_FILL)

    def _markLegacyTargetComplete(self, cell):
        """
        Change a legacy target marker to green when completed.
        """
        if cell is None or self.legacyTargetImages is None:
            return
        x, y = cell
        if x >= len(self.legacyTargetImages) or y >= len(self.legacyTargetImages[x]):
            return
        img = self.legacyTargetImages[x][y]
        if img is None:
            return
        # img is [glow, inner, label]
        glow, inner, label = img
        edit(glow, ("fill", COMPLETED_OUTLINE), ("outline", COMPLETED_OUTLINE))
        edit(inner, ("fill", COMPLETED_FILL), ("outline", COMPLETED_FILL))
        changeText(label, "OK")

    def _updateMissionElements(self, state):
        """
        Update mission markers when objects are collected or repaired.
        """
        for position, image in self.missionElementImages.items():
            symbol = image["symbol"]
            completed = self._missionElementCompleted(state, position, symbol)
            if completed:
                for detail in image.get("details", []):
                    edit(detail, ("state", "hidden"))
                edit(
                    image["outer"],
                    ("fill", COMPLETED_OUTLINE),
                    ("outline", COMPLETED_OUTLINE),
                )
                edit(
                    image["inner"],
                    ("fill", COMPLETED_FILL),
                    ("outline", COMPLETED_FILL),
                )
                changeText(image["label"], "OK")
            else:
                for detail in image.get("details", []):
                    edit(detail, ("state", "normal"))
                fillColor = self._missionFill(symbol)
                edit(
                    image["outer"],
                    ("fill", MISSION_OUTLINE),
                    ("outline", MISSION_OUTLINE),
                )
                edit(
                    image["inner"],
                    ("fill", fillColor),
                    ("outline", image.get("innerOutline", fillColor)),
                )
                changeText(image["label"], symbol)

    def _missionElementCompleted(self, state, position, symbol):
        """
        Returns True if a mission marker has already been handled.
        """
        if symbol == "D":
            return state.missionType == "diagnostic" and state._win
        if symbol == "M":
            return state.missionType == "module" and state.hasModule
        if symbol == "K":
            return state.missionType == "systems" and state.hasKit
        if symbol == "T":
            return state.missionType == "systems" and position not in state.pendingSystems
        if symbol == "C":
            return (
                state._win
                and state.missionType in ["module", "systems"]
                and position == state.controlPosition
            )
        return False

    # ========================================
    # ROBOT AGENT
    # ========================================

    def _drawAgents(self, state):
        """
        Draw all agents (typically just one robot).
        """
        self.agentImages = []
        for _, agentState in enumerate(state.agentStates):
            parts = self._drawRobot(agentState)
            self.agentImages.append((agentState, parts))
        refresh()

    def _getPos(self, agentState):
        if agentState.configuration is None:
            return (-1000, -1000)
        return agentState.getPosition()

    def _getDir(self, agentState):
        if agentState.configuration is None:
            return Directions.STOP
        return agentState.configuration.getDirection()

    def _drawRobot(self, agentState):
        """
        Draw robot as professional station maintenance unit.
        Wrapper that extracts position/direction from agentState.
        """
        pos = self._getPos(agentState)
        dirn = self._getDir(agentState)
        return self._drawRobotAtPosition(pos, dirn)

    def _drawRobotAtPosition(self, pos, dirn):
        """
        Draw robot at specific position and direction.
        - Compact maintenance body
        - Side treads
        - Directional sensor array
        - Status indicator and direction arrow
        """
        screen = self.to_screen(pos)
        g = self.gridSize
        parts = []

        # Soft shadow
        shadow = circle(
            (screen[0] + 0.03 * g, screen[1] + 0.05 * g),
            0.38 * g,
            ROBOT_SHADOW,
            ROBOT_SHADOW,
        )
        parts.append(shadow)

        # Side treads
        leftTread = self._rectangle(
            (screen[0] - 0.27 * g, screen[1] + 0.02 * g),
            0.06 * g,
            0.27 * g,
            ROBOT_OUTLINE,
            ROBOT_TREAD,
        )
        rightTread = self._rectangle(
            (screen[0] + 0.27 * g, screen[1] + 0.02 * g),
            0.06 * g,
            0.27 * g,
            ROBOT_OUTLINE,
            ROBOT_TREAD,
        )
        parts.extend([leftTread, rightTread])

        # Main armored body
        body = self._rectangle(
            screen,
            0.25 * g,
            0.30 * g,
            ROBOT_OUTLINE,
            ROBOT_BODY,
            width=2,
        )
        parts.append(body)

        # Central service panel
        panel = self._rectangle(
            (screen[0], screen[1] + 0.05 * g),
            0.15 * g,
            0.15 * g,
            ROBOT_ACCENT,
            ROBOT_ACCENT,
        )
        parts.append(panel)

        # Sensor visor
        visor = self._rectangle(
            (screen[0], screen[1] - 0.16 * g),
            0.17 * g,
            0.055 * g,
            ROBOT_VISOR,
            ROBOT_VISOR,
        )
        parts.append(visor)

        # Small service arms
        parts.append(
            line(
                (screen[0] - 0.25 * g, screen[1] - 0.02 * g),
                (screen[0] - 0.40 * g, screen[1] - 0.12 * g),
                ROBOT_OUTLINE,
                width=2,
            )
        )
        parts.append(
            line(
                (screen[0] + 0.25 * g, screen[1] - 0.02 * g),
                (screen[0] + 0.40 * g, screen[1] - 0.12 * g),
                ROBOT_OUTLINE,
                width=2,
            )
        )

        # Directional sensors (3 dots pointing in movement direction)
        sensors = self._getSensorPositions(screen, dirn)
        for sx, sy in sensors:
            sensor = circle((sx, sy), 0.045 * g, ROBOT_SENSOR, ROBOT_SENSOR)
            parts.append(sensor)

        # Direction arrow and status light
        parts.append(self._drawRobotDirectionArrow(screen, dirn))
        status = circle(
            (screen[0], screen[1] + 0.20 * g),
            0.045 * g,
            ROBOT_LIGHT,
            ROBOT_LIGHT,
        )
        parts.append(status)

        return parts

    def _drawRobotDirectionArrow(self, center, direction):
        """
        Draw a small arrow showing where the robot is facing.
        """
        cx, cy = center
        g = self.gridSize

        if direction == Directions.SOUTH:
            points = [
                (cx, cy + 0.02 * g),
                (cx - 0.09 * g, cy - 0.11 * g),
                (cx + 0.09 * g, cy - 0.11 * g),
            ]
        elif direction == Directions.WEST:
            points = [
                (cx - 0.10 * g, cy - 0.04 * g),
                (cx + 0.04 * g, cy - 0.13 * g),
                (cx + 0.04 * g, cy + 0.05 * g),
            ]
        elif direction == Directions.EAST:
            points = [
                (cx + 0.10 * g, cy - 0.04 * g),
                (cx - 0.04 * g, cy - 0.13 * g),
                (cx - 0.04 * g, cy + 0.05 * g),
            ]
        else:
            points = [
                (cx, cy - 0.19 * g),
                (cx - 0.09 * g, cy - 0.04 * g),
                (cx + 0.09 * g, cy - 0.04 * g),
            ]

        return polygon(
            points,
            ROBOT_LIGHT,
            ROBOT_LIGHT,
            filled=1,
            smoothed=0,
        )

    def _getSensorPositions(self, center, direction):
        """
        Calculate sensor positions based on robot direction.
        """
        cx, cy = center
        offset = 0.40 * self.gridSize
        side = 0.12 * self.gridSize

        if direction == Directions.NORTH:
            return [
                (cx, cy - offset),
                (cx - side, cy - offset * 0.75),
                (cx + side, cy - offset * 0.75),
            ]
        elif direction == Directions.SOUTH:
            return [
                (cx, cy + offset),
                (cx - side, cy + offset * 0.75),
                (cx + side, cy + offset * 0.75),
            ]
        elif direction == Directions.WEST:
            return [
                (cx - offset, cy),
                (cx - offset * 0.75, cy - side),
                (cx - offset * 0.75, cy + side),
            ]
        elif direction == Directions.EAST:
            return [
                (cx + offset, cy),
                (cx + offset * 0.75, cy - side),
                (cx + offset * 0.75, cy + side),
            ]
        else:
            return [
                (cx, cy - offset),
                (cx - side, cy - offset * 0.75),
                (cx + side, cy - offset * 0.75),
            ]

    def _moveRobot(self, pos, dirn, parts):
        """
        Move robot by redrawing (simple and clean).
        """
        # Remove old parts
        for p in parts:
            remove_from_screen(p)

        # Redraw at new position
        newParts = self._drawRobotAtPosition(pos, dirn)
        parts[:] = newParts  # Update list in place
        refresh()

    def _renderState(self, state):
        """
        Render a previously generated mission state.
        """
        agentState = state.agentStates[0]
        _, parts = self.agentImages[0]
        self._moveRobot(self._getPos(agentState), self._getDir(agentState), parts)
        self.agentImages[0] = (agentState, parts)

        if getattr(state, "missionType", "legacy") == "legacy":
            self._redrawLegacyTargets(state)
        else:
            self._updateMissionElements(state)

        cost = getattr(state, "cumulativeCost", 0)
        self.infoPane.updateCost(cost)
        self.infoPane.updateMissionStatus(state)
        refresh()

    def _redrawLegacyTargets(self, state):
        """
        Redraw legacy targets when step-by-step mode moves backward.
        """
        if self.legacyTargetImages is None:
            return

        for x, col in enumerate(self.legacyTargetImages):
            for y, img in enumerate(col):
                if img is None:
                    continue
                glow, inner, label = img
                if state.legacyTargets[x][y]:
                    edit(glow, ("fill", MISSION_OUTLINE), ("outline", MISSION_OUTLINE))
                    edit(inner, ("fill", SYSTEM_FILL), ("outline", SYSTEM_FILL))
                    changeText(label, "S")
                else:
                    edit(
                        glow,
                        ("fill", COMPLETED_OUTLINE),
                        ("outline", COMPLETED_OUTLINE),
                    )
                    edit(inner, ("fill", COMPLETED_FILL), ("outline", COMPLETED_FILL))
                    changeText(label, "OK")

    def _waitForStepMode(self):
        """
        Let the user browse already generated frames in step-by-step mode.
        """
        if not self._step_mode_message_shown:
            print(
                "MODO PASO A PASO: Derecha avanza, Izquierda retrocede. "
                "Otras teclas avanzan en el último cuadro."
            )
            self._step_mode_message_shown = True

        while True:
            key = self._waitForStepKey()

            if self._isLeftKey(key):
                if self._historyIndex > 0:
                    self._historyIndex -= 1
                    self._renderState(self._stateHistory[self._historyIndex])
                continue

            if self._isRightKey(key):
                if self._historyIndex < len(self._stateHistory) - 1:
                    self._historyIndex += 1
                    self._renderState(self._stateHistory[self._historyIndex])
                    continue
                return

            if self._historyIndex < len(self._stateHistory) - 1:
                self._historyIndex += 1
                self._renderState(self._stateHistory[self._historyIndex])
                continue
            return

    def _waitForStepKey(self):
        """
        Wait for a new key press and return its Tk key symbol.
        """
        while True:
            keys_pressed()
            waiting = list(keys_waiting())
            if waiting:
                return waiting[-1]
            sleep(0.05)

    def _isLeftKey(self, key):
        return key in ["Left", "a", "A"]

    def _isRightKey(self, key):
        return key in ["Right", "d", "D", "space", "Return"]

    # ========================================
    # UPDATE LOOP
    # ========================================

    def update(self, newState):
        """
        Update display with new mission state.
        """
        self._stateHistory = self._stateHistory[: self._historyIndex + 1]
        self._stateHistory.append(newState)
        self._historyIndex = len(self._stateHistory) - 1
        self._renderState(newState)

        if self.frameTime < 0:
            self._waitForStepMode()
        else:
            sleep(self.frameTime)


# ========================================
# UTILITY FUNCTIONS
# ========================================


def add(x, y):
    """Add two coordinate tuples."""
    return (x[0] + y[0], x[1] + y[1])
