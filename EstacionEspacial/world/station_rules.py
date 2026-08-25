from world.game import Actions
from algorithms.utils import nearestPoint


class StationRules:
    """
    These rules manage how the robot interacts with the station.
    """

    ROBOT_SPEED = 1

    @staticmethod
    def getLegalActions(state):
        """
        Returns a list of possible actions.
        """
        return Actions.getPossibleActions(
            state.getRobotState().configuration, state.data.layout.walls
        )

    @staticmethod
    def applyAction(state, action):
        """
        Edits the state to reflect the results of the action.
        """
        legal = StationRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Illegal action " + str(action))

        robotState = state.data.agentStates[0]

        # Update Configuration
        vector = Actions.directionToVector(action, StationRules.ROBOT_SPEED)
        robotState.configuration = robotState.configuration.generateSuccessor(
            vector
        )

        # Update mission state if the robot reached a relevant cell.
        next_pos = robotState.configuration.getPosition()
        nearest = nearestPoint(next_pos)
        if abs(nearest[0] - next_pos[0]) + abs(nearest[1] - next_pos[1]) <= 0.5:
            StationRules.updateMission(nearest, state)

    @staticmethod
    def updateMission(position, state):
        """
        Applies the station mission interaction at the given position.
        """
        missionType = getattr(state.data, "missionType", "legacy")

        if missionType == "diagnostic":
            StationRules.checkDiagnosticTerminal(position, state)
        elif missionType == "module":
            StationRules.checkModuleRepair(position, state)
        elif missionType == "systems":
            StationRules.checkSystemRepair(position, state)
        else:
            StationRules.completeLegacyTarget(position, state)

    @staticmethod
    def checkDiagnosticTerminal(position, state):
        """
        Complete the diagnostic mission when the robot reaches D.
        """
        if position == state.data.diagnosticTerminal and not state.data._lose:
            state.data.missionEvent = ("diagnostic", position)
            state.data._win = True

    @staticmethod
    def checkModuleRepair(position, state):
        """
        Pick up M and complete the mission at C after carrying it.
        """
        if position == state.data.modulePosition and not state.data.hasModule:
            state.data.hasModule = True
            state.data.missionEvent = ("module", position)

        if (
            position == state.data.controlPosition
            and state.data.hasModule
            and not state.data._lose
        ):
            state.data.missionEvent = ("control", position)
            state.data._win = True

    @staticmethod
    def checkSystemRepair(position, state):
        """
        Pick up K, repair pending T systems, and complete the mission at C.
        """
        if position == state.data.kitPosition and not state.data.hasKit:
            state.data.hasKit = True
            state.data.missionEvent = ("kit", position)

        if state.data.hasKit and position in state.data.pendingSystems:
            state.data.pendingSystems = tuple(
                system for system in state.data.pendingSystems if system != position
            )
            state.data.repairedCount += 1
            state.data.missionEvent = ("system", position)

        if (
            position == state.data.controlPosition
            and state.data.hasKit
            and len(state.data.pendingSystems) == 0
            and not state.data._lose
        ):
            state.data.missionEvent = ("control", position)
            state.data._win = True

    @staticmethod
    def completeLegacyTarget(position, state):
        """
        Complete a target from older layouts that still use S markers.
        """
        x, y = position

        # Complete legacy target if present.
        if state.data.legacyTargets[x][y]:
            state.data.completedLegacyCount += 1
            state.data.legacyTargetCompleted = (x, y)
            state.data.legacyTargets = state.data.legacyTargets.copy()
            state.data.legacyTargets[x][y] = False

            # Check if the legacy mission is complete.
            remainingTargets = state.getNumLegacyTargets()
            if remainingTargets == 0 and not state.data._lose:
                state.data._win = True
