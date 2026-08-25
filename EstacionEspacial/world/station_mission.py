from world.game import Game
from world.station_state import StationState


class StationMission:
    """
    These rules manage the control flow of the station mission.
    """

    def newMission(self, layout, stationAgent, display, quiet=False, catchExceptions=False):
        """
        Create a new station mission.
        """
        agents = [stationAgent]
        initState = StationState()
        initState.initialize(layout)

        if not getattr(display, "deferExecutionSummary", False):
            print("Misión:", initState.data.getObjectiveText())
            print("Tipo de misión:", initState.getMissionType())

        mission = Game(agents, display, self, catchExceptions=catchExceptions)
        mission.state = initState
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return mission

    def process(self, state, mission):
        """
        Checks to see whether it is time to end the mission.
        """
        if state.isWin():
            self.win(state, mission)
        if state.isLose():
            self.lose(state, mission)

    def win(self, state, mission):
        if not self.quiet and not getattr(mission.display, "deferExecutionSummary", False):
            print("¡Misión completada! Costo: %d" % state.data.cumulativeCost)
        mission.gameOver = True

    def lose(self, state, mission):
        if not self.quiet and not getattr(mission.display, "deferExecutionSummary", False):
            print("Misión fallida. Costo: %d" % state.data.cumulativeCost)
        mission.gameOver = True

    def getProgress(self, mission):
        state = mission.state

        if state.isWin():
            return 1.0

        if state.getMissionType() == "diagnostic":
            return 0.0

        if state.getMissionType() == "module":
            return 0.5 if state.hasModule() else 0.0

        if state.getMissionType() == "systems":
            totalSteps = state.getTotalSystems() + 2
            completedSteps = state.getRepairedCount()
            if state.hasKit():
                completedSteps += 1
            return float(completedSteps) / totalSteps

        totalLegacyTargets = self.initialState.getNumLegacyTargets()
        if totalLegacyTargets == 0:
            return 1.0
        return (
            float(totalLegacyTargets - state.getNumLegacyTargets())
            / totalLegacyTargets
        )
