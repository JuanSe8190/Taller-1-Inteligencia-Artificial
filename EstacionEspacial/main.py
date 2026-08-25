import world.station_layout as station_layout
import sys
import time
import pickle
from optparse import OptionParser
from world.station_mission import StationMission


def readCommand(argv):
    """
    Processes the command used to run main from the command line.
    """

    usageStr = """
    RECOMMENDED: python menu.py

    USAGE:      python main.py -p PROBLEM -f FUNCTION -l LAYOUT_FILE [options]
    EXAMPLES:
      python main.py -p DiagnosticProblem -f tinyDiagnosticSearch -l tinyDiagnostic
      python main.py -p DiagnosticProblem -f breadthFirstSearch -l radiationShortcut
      python main.py -p ModuleRepairProblem -f uniformCostSearch -l moduleVault
      python main.py -p SystemRepairProblem -f aStarSearch -h systemRepairHeuristic -l finalMaintenanceComplex
    """
    parser = OptionParser(usageStr, add_help_option=False)
    parser.add_option(
        "--help",
        action="help",
        help="Show this message and exit",
    )

    PROBLEM_CHOICES = (
        "DiagnosticProblem",
        "ModuleRepairProblem",
        "SystemRepairProblem",
    )
    parser.add_option(
        "-p",
        "--problem",
        dest="problem",
        help="Problem type (required). One of: %s" % ", ".join(PROBLEM_CHOICES),
        metavar="PROBLEM",
    )
    parser.add_option(
        "-f",
        "--function",
        dest="function",
        help="Search function name (required). e.g. tinyDiagnosticSearch, breadthFirstSearch, aStarSearch",
        metavar="FUNCTION",
    )
    parser.add_option(
        "-h",
        "--heuristic",
        dest="heuristic",
        help=default("Heuristic function name (for A*). e.g. nullHeuristic, manhattanHeuristic"),
        metavar="HEURISTIC",
        default="nullHeuristic",
    )
    parser.add_option(
        "-l",
        "--layout",
        dest="layout",
        help="Layout file to load (required)",
        metavar="LAYOUT_FILE",
    )
    parser.add_option(
        "-t",
        "--textGraphics",
        action="store_true",
        dest="textGraphics",
        help="Display output as text only",
        default=False,
    )
    parser.add_option(
        "-q",
        "--quietTextGraphics",
        action="store_true",
        dest="quietGraphics",
        help="Generate minimal output and no graphics",
        default=False,
    )
    parser.add_option(
        "-z",
        "--zoom",
        type="float",
        dest="zoom",
        help=default("Zoom the size of the graphics window"),
        default=1.0,
    )
    parser.add_option(
        "-r",
        "--recordActions",
        action="store_true",
        dest="record",
        help="Writes mission histories to a file",
        default=False,
    )
    parser.add_option(
        "-x",
        "--frameTime",
        dest="frameTime",
        type="float",
        help=default("Time to delay between frames; <0 uses Left/Right step mode"),
        default=0.25,
    )
    parser.add_option(
        "-c",
        "--catchExceptions",
        action="store_true",
        dest="catchExceptions",
        help="Turns on exception handling during missions",
        default=False,
    )

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception("Command line input not understood: " + str(otherjunk))

    if not options.problem:
        parser.error("-p/--problem is required. Choose one of: %s" % ", ".join(PROBLEM_CHOICES))
    if options.problem not in PROBLEM_CHOICES:
        parser.error(
            "Invalid problem type '%s'. Choose one of: %s"
            % (options.problem, ", ".join(PROBLEM_CHOICES))
        )
    if not options.function:
        parser.error("-f/--function is required")
    if not options.layout:
        parser.error("-l/--layout is required")

    args = dict()

    # Choose a layout
    args["layout"] = station_layout.getLayout(options.layout)
    if args["layout"] is None:
        raise Exception("The layout " + options.layout + " cannot be found")

    deferSummaryOutput = options.textGraphics
    if not deferSummaryOutput:
        print("RobotPositions:", args["layout"].agentPositions)
        print("MissionSymbols:", getMissionSymbols(args["layout"]))

    # Choose a station maintenance agent
    robotAgentType = loadAgent("SearchAgent")
    robotAgent = robotAgentType(
        fn=options.function,
        prob=options.problem,
        heuristic=options.heuristic,
        deferOutput=deferSummaryOutput,
    )
    args["robotAgent"] = robotAgent

    # Choose a display format
    if options.quietGraphics:
        import view.text_display as text_display

        args["display"] = text_display.NullGraphics()
    elif options.textGraphics:
        import view.text_display as text_display

        text_display.SLEEP_TIME = options.frameTime
        args["display"] = text_display.StationGraphics()
    else:
        import view.graphics_display as graphics_display

        args["display"] = graphics_display.StationGraphics(
            options.zoom, frameTime=options.frameTime
        )

    if hasattr(args["display"], "setSummaryContext"):
        args["display"].setSummaryContext(args["layout"], robotAgent)

    args["record"] = options.record
    args["catchExceptions"] = options.catchExceptions

    return args


def default(str_val):
    return str_val + " [Default: %default]"


def getMissionSymbols(layout):
    """
    Returns the positions of the station mission symbols in the raw layout.
    """
    return {
        symbol: layout.getSymbolPositions(symbol)
        for symbol in ["D", "C", "M", "K", "T"]
    }


def loadAgent(agentName):
    """
    Looks through algorithms/agents.py for the right agent.
    """
    try:
        module = __import__("algorithms.agents", fromlist=[agentName])
    except ImportError:
        raise Exception("The agents module could not be imported.")

    if agentName in dir(module):
        return getattr(module, agentName)

    raise Exception(
        "The agent " + agentName + " is not specified in algorithms/agents.py."
    )


def runMission(layout, robotAgent, display, record, catchExceptions=False):
    """
    Run station maintenance missions.
    """
    import __main__

    __main__.__dict__["_display"] = display

    stationMission = StationMission()

    episode = stationMission.newMission(
        layout,
        robotAgent,
        display,
        False,
        catchExceptions,
    )
    episode.run()

    if record:
        fname = ("recorded-episode") + "-".join(
            [str(t) for t in time.localtime()[1:6]]
        )
        f = open(fname, "wb")
        components = {"layout": layout, "actions": episode.moveHistory}
        pickle.dump(components, f)
        f.close()

    return episode


if __name__ == "__main__":
    """
    The main function is called when main.py is run from the command line.
    """
    args = readCommand(sys.argv[1:])
    runMission(**args)
