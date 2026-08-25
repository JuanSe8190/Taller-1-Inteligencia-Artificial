"""
Textual launcher for Taller 1: Station Maintenance.

The app lets students select the workshop point, click a layout, adjust the
general execution settings, and launch main.py with the selected arguments.
main.py remains the command-line fallback when the TUI dependency is not
available on a particular computer.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
MAIN_FILE = PROJECT_DIR / "main.py"
HEURISTICS_FILE = PROJECT_DIR / "algorithms" / "heuristics.py"


WORKSHOP_POINTS = [
    {
        "title": "Punto 1 - DFS",
        "subtitle": "Diagnostico",
        "description": "Encontrar cualquier ruta valida hasta D.",
        "problem": "DiagnosticProblem",
        "layoutFolder": "diagnostic",
        "algorithm": ("depthFirstSearch", "DFS"),
        "heuristics": [],
    },
    {
        "title": "Punto 2 - BFS",
        "subtitle": "Diagnostico",
        "description": "Encontrar la ruta con menor numero de movimientos.",
        "problem": "DiagnosticProblem",
        "layoutFolder": "diagnostic",
        "algorithm": ("breadthFirstSearch", "BFS"),
        "heuristics": [],
    },
    {
        "title": "Punto 3 - UCS",
        "subtitle": "Diagnostico con costos",
        "description": "Comparar menor profundidad contra menor costo acumulado.",
        "problem": "DiagnosticProblem",
        "layoutFolder": "diagnostic",
        "algorithm": ("uniformCostSearch", "UCS"),
        "heuristics": [],
    },
    {
        "title": "Punto 4 - UCS Modulo",
        "subtitle": "Modulo obligatorio",
        "description": "Recoger M y terminar en C con costo dependiente del estado.",
        "problem": "ModuleRepairProblem",
        "layoutFolder": "module",
        "algorithm": ("uniformCostSearch", "UCS"),
        "heuristics": [],
    },
    {
        "title": "Punto 5 - A*",
        "subtitle": "Reparacion de sistemas",
        "description": "Recoger K, reparar todos los T y volver a C.",
        "problem": "SystemRepairProblem",
        "layoutFolder": "systems",
        "algorithm": ("aStarSearch", "A*"),
        "heuristics": [
            ("systemRepairHeuristic", "systemRepairHeuristic"),
            ("nullHeuristic", "nullHeuristic"),
        ],
    },
]


DISPLAY_MODES = [
    ("graphics", "Ventana grafica"),
    ("text", "Modo texto"),
    ("quiet", "Sin animacion"),
]

SPEEDS = [
    (0.03, "Rapida"),
    (0.10, "Normal"),
    (0.25, "Lenta"),
    (-1.0, "Paso a paso"),
]

ZOOMS = [
    (0.75, "Pequeño"),
    (1.00, "Normal"),
    (1.25, "Grande"),
    (1.50, "Muy grande"),
]


try:
    from rich.markup import escape
    from textual import on
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
    from textual.message import Message
    from textual.widgets import Button, Footer, Header, Input, Static

    TEXTUAL_AVAILABLE = True
except ModuleNotFoundError:
    TEXTUAL_AVAILABLE = False


def main() -> int:
    """
    Runs the Textual launcher, or prints a clear fallback message.
    """
    if "--check" in sys.argv:
        validate_menu_data()
        return 0

    if not TEXTUAL_AVAILABLE:
        print_missing_textual_message()
        return 1

    StationMenuApp().run()
    return 0


def available_layouts(folder):
    """
    Returns available layouts found in the corresponding folder.
    """
    folder_path = PROJECT_DIR / "layouts" / folder
    infos = [layout_info(folder, path.stem) for path in folder_path.glob("*.lay")]

    if folder == "systems":
        infos.sort(
            key=lambda info: (
                info["systems"],
                info["width"] * info["height"],
                info["height"],
                info["width"],
                info["name"].lower(),
            )
        )
    else:
        infos.sort(
            key=lambda info: (
                info["width"] * info["height"],
                info["height"],
                info["width"],
                info["name"].lower(),
            )
        )

    return [info["name"] for info in infos]


def layout_path(folder, name):
    """
    Returns the full path for a layout name.
    """
    return PROJECT_DIR / "layouts" / folder / ("%s.lay" % name)


def layout_info(folder, name):
    """
    Returns metadata shown in the launcher.
    """
    path = layout_path(folder, name)
    rows = path.read_text().splitlines()
    text = "".join(rows)
    width = len(rows[0]) if rows else 0
    height = len(rows)
    return {
        "name": name,
        "folder": folder,
        "width": width,
        "height": height,
        "systems": text.count("T"),
        "robots": text.count("R"),
        "diagnostics": text.count("D"),
        "modules": text.count("M"),
        "kits": text.count("K"),
        "controls": text.count("C"),
        "walls": text.count("%"),
        "open": sum(1 for char in text if char != "%"),
        "path": path,
        "rows": rows,
    }


def layout_meta_label(point, info):
    """
    Returns one-line metadata for a layout card.
    """
    size = "%dx%d" % (info["width"], info["height"])
    if point["layoutFolder"] == "systems":
        return "%s | %d sistemas" % (size, info["systems"])
    if point["layoutFolder"] == "module":
        return "%s | R-M-C" % size
    return "%s | R-D" % size


def compact_label(text, max_length=24):
    """
    Keeps card labels on one readable line in narrow terminals.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def point_uses_heuristic(point):
    """
    Returns True when the selected algorithm accepts a heuristic.
    """
    algorithm_name = point["algorithm"][0]
    return algorithm_name == "aStarSearch" or bool(point["heuristics"])


def is_heuristic_name(name):
    """
    Recognizes common heuristic naming conventions.
    """
    lowered = name.lower()
    return lowered.endswith("heuristic") or lowered.endswith("heuristica")


def heuristic_function_names():
    """
    Returns function names defined in algorithms/heuristics.py.
    """
    try:
        tree = ast.parse(HEURISTICS_FILE.read_text())
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None

    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def discovered_heuristics():
    """
    Finds heuristics whose names end in Heuristic or Heuristica.
    """
    names = heuristic_function_names()
    if names is None:
        return []

    ordered = []
    try:
        tree = ast.parse(HEURISTICS_FILE.read_text())
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []

    for node in tree.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and is_heuristic_name(node.name)
        ):
            ordered.append((node.name, node.name))
    return ordered


def heuristic_options(point):
    """
    Returns default heuristics plus auto-detected student heuristics.
    """
    if not point_uses_heuristic(point):
        return []

    options = []
    seen = set()

    for value, label in point["heuristics"] + discovered_heuristics():
        if value not in seen:
            options.append((value, label))
            seen.add(value)

    return options


def command_to_text(command):
    """
    Returns a readable command-line representation.
    """
    parts = []
    for part in command:
        text = str(part)
        if " " in text:
            parts.append('"%s"' % text)
        else:
            parts.append(text)
    return " ".join(parts)


def command_to_multiline_text(command):
    """
    Returns a compact multi-line command preview for the launcher.
    """
    if len(command) <= 2:
        return command_to_text(command)

    lines = [command_to_text(command[:2])]
    index = 2

    while index < len(command):
        current = str(command[index])
        if (
            current.startswith("-")
            and index + 1 < len(command)
            and not str(command[index + 1]).startswith("-")
        ):
            lines.append("  %s %s" % (current, command_to_text([command[index + 1]])))
            index += 2
        else:
            lines.append("  %s" % command_to_text([command[index]]))
            index += 1

    return "\n".join(lines)


def validate_menu_data():
    """
    Lightweight validation for the launcher data and available layouts.
    """
    total = 0
    for point in WORKSHOP_POINTS:
        layouts = available_layouts(point["layoutFolder"])
        if not layouts:
            raise SystemExit("No layouts found for %s" % point["title"])
        for layout in layouts:
            info = layout_info(point["layoutFolder"], layout)
            if len({len(row) for row in info["rows"]}) != 1:
                raise SystemExit("%s has inconsistent row widths" % layout)
            if info["robots"] != 1:
                raise SystemExit("%s must contain exactly one R" % layout)
            total += 1
        print("%-28s %2d layouts" % (point["title"], len(layouts)))
    print("OK: %d layouts available." % total)


def print_missing_textual_message():
    """
    Explains how to install the TUI dependency and how to use main.py directly.
    """
    print()
    print("La interfaz de terminal usa Textual.")
    print("Textual no esta instalado en este entorno.")
    print()
    print("Instalacion recomendada:")
    print("  python -m pip install -r requirements.txt")
    print()
    print("Respaldo por comandos:")
    print("  python main.py -p DiagnosticProblem -f breadthFirstSearch -l radiationShortcut")
    print("  python main.py -p ModuleRepairProblem -f uniformCostSearch -l moduleVault")
    print(
        "  python main.py -p SystemRepairProblem -f aStarSearch "
        "-h systemRepairHeuristic -l finalMaintenanceComplex"
    )
    print()


if TEXTUAL_AVAILABLE:

    class PointCard(Static):
        """
        Clickable card for a workshop point.
        """

        class Selected(Message):
            def __init__(self, index):
                self.index = index
                super().__init__()

        def __init__(self, index, point):
            self.index = index
            self.point = point
            algorithm_name, algorithm_label = point["algorithm"]
            content = (
                "[bold #f0c040]%s[/]\n"
                "[#58a6ff]%s[/] [dim]| %s[/]"
                % (
                    escape(point["title"]),
                    escape(point["subtitle"]),
                    escape(algorithm_label),
                )
            )
            super().__init__(content, classes="point-card")

        def on_click(self, event=None):
            self.post_message(self.Selected(self.index))


    class LayoutCard(Static):
        """
        Clickable card for one layout.
        """

        class Selected(Message):
            def __init__(self, layout_name):
                self.layout_name = layout_name
                super().__init__()

        def __init__(self, point, info):
            self.layout_name = info["name"]
            meta = layout_meta_label(point, info)
            content = (
                "[bold]%s[/]\n"
                "[dim]%s[/]"
                % (escape(compact_label(info["name"])), escape(meta))
            )
            super().__init__(content, classes="layout-card")

        def on_click(self, event=None):
            self.post_message(self.Selected(self.layout_name))


    class OptionCard(Static):
        """
        Clickable setting option.
        """

        class Selected(Message):
            def __init__(self, option_group, option_value):
                self.option_group = option_group
                self.option_value = option_value
                super().__init__()

        def __init__(self, group, value, label):
            self.option_group = group
            self.option_value = value
            content = "[bold]%s[/]" % escape(label)
            super().__init__(content, classes="option-card")

        def on_click(self, event=None):
            self.post_message(self.Selected(self.option_group, self.option_value))


    CSS = """
    Screen {
        background: #0d1117;
        color: #e6edf3;
    }

    #shell {
        height: 1fr;
        layout: horizontal;
    }

    .title-bar {
        height: 3;
        padding: 0 2;
        background: #161b22;
        border-bottom: solid #30363d;
        content-align: left middle;
    }

    .panel {
        background: #0d1117;
        border: solid #30363d;
        padding: 1;
        height: 100%;
    }

    #point-panel {
        width: 30;
        min-width: 26;
    }

    #layout-panel {
        width: 1fr;
    }

    #settings-panel {
        width: 36;
        min-width: 32;
    }

    .section-title {
        height: 2;
        color: #f0c040;
        text-style: bold;
    }

    .setting-label {
        height: 1;
        margin-top: 1;
        color: #58a6ff;
        text-style: bold;
    }

    #point-list {
        height: 1fr;
    }

    #settings-scroll {
        height: 1fr;
    }

    #layout-grid {
        height: 1fr;
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr;
        grid-rows: 4;
        grid-gutter: 1;
        overflow-y: auto;
    }

    .point-card {
        height: 4;
        padding: 0 1;
        margin-bottom: 1;
        border: solid #21262d;
        background: #161b22;
    }

    .layout-card {
        height: 4;
        min-height: 4;
        padding: 0 1;
        border: solid #21262d;
        background: #161b22;
    }

    .option-card {
        height: 3;
        padding: 0 1;
        border: solid #21262d;
        background: #161b22;
        content-align: center middle;
    }

    .point-card:hover,
    .layout-card:hover,
    .option-card:hover {
        border: solid #58a6ff;
        background: #1c2128;
    }

    .--selected {
        border: solid #f0c040;
        background: #1c2836;
    }

    #selected-info {
        height: auto;
        min-height: 6;
        padding: 0 1;
        border: solid #21262d;
        background: #0a0f16;
    }

    #display-options,
    #speed-options,
    #zoom-options,
    #heuristic-options {
        height: auto;
        layout: grid;
        grid-size: 2;
        grid-gutter: 1;
    }

    #heuristic-options {
        grid-size: 1;
    }

    #display-options {
        grid-size: 1;
    }

    #heuristic-input {
        height: 3;
        margin-bottom: 1;
        border: solid #21262d;
        background: #0a0f16;
    }

    #custom-heuristic-help {
        height: auto;
        color: #8b949e;
    }

    #command-preview {
        height: auto;
        min-height: 9;
        padding: 0 1;
        margin-top: 1;
        border: dashed #30363d;
        background: #0a0f16;
        color: #8b949e;
    }

    #action-buttons {
        height: auto;
        align: center middle;
    }

    .action-button {
        width: 24;
    }

    #status-line {
        height: auto;
        min-height: 3;
        padding: 0 1;
        margin-top: 1;
        color: #3fb950;
    }

    Button {
        height: 3;
        margin-top: 1;
        border: solid #30363d;
    }
    """


    class StationMenuApp(App):
        """
        Textual application for selecting and launching workshop runs.
        """

        TITLE = "Taller 1: Busqueda con y sin informacion"
        SUB_TITLE = "Robot de mantenimiento en estacion espacial"
        CSS = CSS
        CTRL_C_QUIT = True
        BINDINGS = [
            Binding("q", "quit", "Salir"),
            Binding("r", "run", "Ejecutar"),
            Binding("ctrl+c", "quit", "Salir", show=False),
        ]

        def __init__(self):
            super().__init__()
            self.point_index = 0
            self.layout_name = available_layouts(self.current_point["layoutFolder"])[0]
            self.display_mode = "graphics"
            self.frame_time = 0.25
            self.zoom = 1.00
            self.heuristic = "systemRepairHeuristic"
            self.custom_heuristic = ""

        @property
        def current_point(self):
            return WORKSHOP_POINTS[self.point_index]

        @property
        def current_layouts(self):
            point = self.current_point
            return available_layouts(point["layoutFolder"])

        @property
        def current_algorithm(self):
            return self.current_point["algorithm"][0]

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            yield Static(
                "  [bold #f0c040]TALLER 1[/]  "
                "[#58a6ff]Busqueda con y sin informacion[/]  "
                "[dim]Selecciona punto, mapa y configuracion; R ejecuta.[/]",
                classes="title-bar",
            )
            with Horizontal(id="shell"):
                with Vertical(id="point-panel", classes="panel"):
                    yield Static("PUNTOS DEL TALLER", classes="section-title")
                    yield ScrollableContainer(id="point-list")
                with Vertical(id="layout-panel", classes="panel"):
                    yield Static("", id="layout-title", classes="section-title")
                    yield ScrollableContainer(id="layout-grid")
                with Vertical(id="settings-panel", classes="panel"):
                    yield Static("CONFIGURACION", classes="section-title")
                    with ScrollableContainer(id="settings-scroll"):
                        yield Static("", id="selected-info")
                        yield Static("Modo de animacion", classes="setting-label")
                        yield Container(id="display-options")
                        yield Static("Velocidad", classes="setting-label")
                        yield Container(id="speed-options")
                        yield Static("Tamano", classes="setting-label")
                        yield Container(id="zoom-options")
                        yield Static("Heuristica", id="heuristic-label", classes="setting-label")
                        yield Container(id="heuristic-options")
                        yield Static(
                            "Nombre manual",
                            id="custom-heuristic-label",
                            classes="setting-label",
                        )
                        yield Input(
                            placeholder="miHeuristica",
                            id="heuristic-input",
                        )
                        yield Static(
                            "Si escribes un nombre aqui, se usa ese al ejecutar.",
                            id="custom-heuristic-help",
                        )
                        yield Static("", id="command-preview")
                        with Container(id="action-buttons"):
                            yield Button(
                                "Ejecutar seleccion",
                                id="run-button",
                                classes="action-button",
                                variant="primary",
                            )
                            yield Button(
                                "Salir",
                                id="quit-button",
                                classes="action-button",
                            )
                        yield Static("", id="status-line")
            yield Footer()

        def on_mount(self):
            self.rebuild_all()

        def rebuild_all(self):
            self.rebuild_points()
            self.rebuild_layouts()
            self.rebuild_options()
            self.refresh_details()

        def clear_container(self, selector):
            container = self.query_one(selector)
            for child in list(container.children):
                child.remove()
            return container

        def rebuild_points(self):
            container = self.clear_container("#point-list")
            for index, point in enumerate(WORKSHOP_POINTS):
                card = PointCard(index, point)
                if index == self.point_index:
                    card.add_class("--selected")
                container.mount(card)

        def rebuild_layouts(self):
            point = self.current_point
            title = "Selecciona un mapa  |  %s  |  %s" % (
                point["title"],
                point["subtitle"],
            )
            self.query_one("#layout-title", Static).update(escape(title))

            container = self.clear_container("#layout-grid")
            for layout in self.current_layouts:
                info = layout_info(point["layoutFolder"], layout)
                card = LayoutCard(point, info)
                if layout == self.layout_name:
                    card.add_class("--selected")
                container.mount(card)

        def rebuild_options(self):
            self.rebuild_option_group(
                "#display-options",
                "display",
                DISPLAY_MODES,
                self.display_mode,
            )
            self.rebuild_option_group(
                "#speed-options",
                "speed",
                SPEEDS,
                self.frame_time,
            )
            self.rebuild_option_group(
                "#zoom-options",
                "zoom",
                ZOOMS,
                self.zoom,
            )

            heuristic_label = self.query_one("#heuristic-label", Static)
            heuristic_container = self.clear_container("#heuristic-options")
            custom_label = self.query_one("#custom-heuristic-label", Static)
            custom_input = self.query_one("#heuristic-input", Input)
            custom_help = self.query_one("#custom-heuristic-help", Static)
            heuristics = heuristic_options(self.current_point)
            if heuristics:
                heuristic_label.display = True
                heuristic_container.display = True
                custom_label.display = True
                custom_input.display = True
                custom_help.display = True
                if self.heuristic not in [value for value, label in heuristics]:
                    self.heuristic = heuristics[0][0]
                if custom_input.value != self.custom_heuristic:
                    custom_input.value = self.custom_heuristic
                for value, label in heuristics:
                    card = OptionCard("heuristic", value, label)
                    if not self.custom_heuristic and value == self.heuristic:
                        card.add_class("--selected")
                    heuristic_container.mount(card)
            else:
                heuristic_label.display = False
                heuristic_container.display = False
                custom_label.display = False
                custom_input.display = False
                custom_help.display = False

        def rebuild_option_group(self, selector, group, options, selected_value):
            container = self.clear_container(selector)
            for value, label in options:
                card = OptionCard(group, value, label)
                if value == selected_value:
                    card.add_class("--selected")
                container.mount(card)

        def refresh_details(self):
            point = self.current_point
            info = layout_info(point["layoutFolder"], self.layout_name)
            algorithm_name, algorithm_label = point["algorithm"]
            lines = [
                "[bold #f0c040]%s[/]" % escape(self.layout_name),
                "[dim]%s[/]" % escape(layout_meta_label(point, info)),
                "",
                "Problema: [#58a6ff]%s[/]" % escape(point["problem"]),
                "Algoritmo: [#58a6ff]%s[/] ([dim]%s[/])"
                % (escape(algorithm_label), escape(algorithm_name)),
            ]
            if point["layoutFolder"] == "systems":
                lines.append("Sistemas por reparar: [bold]%d[/]" % info["systems"])
                lines.append("Heuristica: [#58a6ff]%s[/]" % escape(self.active_heuristic()))
            self.query_one("#selected-info", Static).update("\n".join(lines))
            self.query_one("#command-preview", Static).update(
                "[bold]Comando generado[/]\n[dim]%s[/]"
                % escape(command_to_multiline_text(self.build_preview_command()))
            )

        def build_command(self):
            point = self.current_point
            command = [
                sys.executable,
                str(MAIN_FILE),
                "-p",
                point["problem"],
                "-f",
                self.current_algorithm,
                "-l",
                self.layout_name,
                "-x",
                str(self.frame_time),
                "-z",
                str(self.zoom),
            ]
            if point_uses_heuristic(point):
                command.extend(["-h", self.active_heuristic()])
            if self.display_mode == "text":
                command.append("-t")
            elif self.display_mode == "quiet":
                command.append("-q")
            return command

        def build_preview_command(self):
            point = self.current_point
            command = [
                "python",
                "main.py",
                "-p",
                point["problem"],
                "-f",
                self.current_algorithm,
                "-l",
                self.layout_name,
                "-x",
                str(self.frame_time),
                "-z",
                str(self.zoom),
            ]
            if point_uses_heuristic(point):
                command.extend(["-h", self.active_heuristic()])
            if self.display_mode == "text":
                command.append("-t")
            elif self.display_mode == "quiet":
                command.append("-q")
            return command

        def active_heuristic(self):
            """
            Returns the selected heuristic, giving priority to manual input.
            """
            if self.custom_heuristic.strip():
                return self.custom_heuristic.strip()
            return self.heuristic

        @on(PointCard.Selected)
        def on_point_selected(self, event):
            self.point_index = event.index
            self.layout_name = self.current_layouts[0]
            self.custom_heuristic = ""
            heuristics = heuristic_options(self.current_point)
            if heuristics:
                self.heuristic = heuristics[0][0]
            self.rebuild_all()

        @on(LayoutCard.Selected)
        def on_layout_selected(self, event):
            self.layout_name = event.layout_name
            self.rebuild_layouts()
            self.refresh_details()

        @on(OptionCard.Selected)
        def on_option_selected(self, event):
            if event.option_group == "display":
                self.display_mode = event.option_value
            elif event.option_group == "speed":
                self.frame_time = event.option_value
            elif event.option_group == "zoom":
                self.zoom = event.option_value
            elif event.option_group == "heuristic":
                self.heuristic = event.option_value
                self.custom_heuristic = ""
                heuristic_input = self.query_one("#heuristic-input", Input)
                heuristic_input.value = ""
            self.rebuild_options()
            self.refresh_details()

        @on(Input.Changed, "#heuristic-input")
        def on_heuristic_input_changed(self, event):
            self.custom_heuristic = event.value.strip()
            self.rebuild_options()
            self.refresh_details()

        @on(Button.Pressed)
        def on_button_pressed(self, event):
            button_id = event.button.id
            if button_id == "run-button":
                self.action_run()
            elif button_id == "quit-button":
                self.action_quit()

        def action_run(self):
            if not self.validate_manual_heuristic():
                return

            command = self.build_command()
            self.query_one("#status-line", Static).update(
                "Ejecutando seleccion. Al cerrar la mision, vuelve aqui."
            )
            with self.suspend():
                print()
                print("Ejecutando:")
                print("  " + command_to_text(command))
                print()
                result = subprocess.run(command, cwd=str(PROJECT_DIR))
                print()
                if result.returncode == 0:
                    print("Ejecucion finalizada.")
                else:
                    print("La ejecucion termino con codigo %d." % result.returncode)
                input("Presiona Enter para volver al menu...")

        def validate_manual_heuristic(self):
            """
            Checks that a manually typed heuristic exists when it can be verified.
            """
            if (
                not point_uses_heuristic(self.current_point)
                or not self.custom_heuristic.strip()
            ):
                return True

            names = heuristic_function_names()
            if names is None or self.custom_heuristic in names:
                return True

            self.query_one("#status-line", Static).update(
                "[red]No existe una funcion llamada %s en algorithms/heuristics.py[/]"
                % escape(self.custom_heuristic)
            )
            return False

        def action_quit(self):
            self.exit()


if __name__ == "__main__":
    sys.exit(main())
